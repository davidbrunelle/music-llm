#!/usr/bin/env python3
"""Parse an Ableton Live .als file and print a structured project summary."""

import gzip
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def get_attr(el, attr, default=""):
    if el is None:
        return default
    return el.get(attr, default)


def find_val(el, path, attr="Value", default=""):
    found = el.find(path)
    if found is None:
        return default
    return found.get(attr, default)


def get_device_name(device_el):
    """Return the display name for a device element."""
    tag = device_el.tag

    # VST3
    vst3 = device_el.find(".//PluginDesc/Vst3PluginInfo/Name")
    if vst3 is not None:
        name = vst3.get("Value", "")
        if name:
            return f"{name} (VST3)"

    # VST2
    vst2 = device_el.find(".//PluginDesc/VstPluginInfo/PlugName")
    if vst2 is not None:
        name = vst2.get("Value", "")
        if name:
            return f"{name} (VST)"

    # Native device — use tag name, strip Ableton namespace noise
    return tag


def get_drum_rack_pads(drum_rack_el):
    """Return a list of pad instrument names from a Drum Rack."""
    pads = []
    for branch in drum_rack_el.findall(".//Branches/DrumBranch"):
        branch_name = find_val(branch, "Name/EffectiveName")
        devices = []
        for device in branch.findall("DeviceChain/Devices/*"):
            devices.append(get_device_name(device))
        pad_label = branch_name if branch_name else "(unnamed pad)"
        if devices:
            pad_label += f" [{', '.join(devices)}]"
        pads.append(pad_label)
    return pads


def parse_track(track_el):
    track_type = track_el.tag  # MidiTrack, AudioTrack, GroupTrack, ReturnTrack
    name = find_val(track_el, ".//Name/EffectiveName")

    devices = []
    for device in track_el.findall("DeviceChain/Devices/*"):
        dev_name = get_device_name(device)
        if device.tag == "DrumGroupDevice":
            pads = get_drum_rack_pads(device)
            devices.append(f"Drum Rack ({len(pads)} pads)")
            for pad in pads:
                devices.append(f"  · {pad}")
        else:
            devices.append(dev_name)

    midi_clips = []
    for clip in track_el.findall(".//MidiClip"):
        clip_name = find_val(clip, "Name")
        loop_end = clip.find("Loop/LoopEnd")
        bars = ""
        if loop_end is not None:
            try:
                bars = f"{float(loop_end.get('Value', 0)) / 4:.1f} bars"
            except (ValueError, TypeError):
                pass
        notes_el = clip.findall(".//KeyTrack/Notes/MidiNoteEvent")
        note_count = len(notes_el)
        label = clip_name if clip_name else "(unnamed)"
        if bars:
            label += f", {bars}"
        if note_count:
            label += f", {note_count} notes"
        midi_clips.append(label)

    audio_clips = []
    for clip in track_el.findall(".//AudioClip"):
        clip_name = find_val(clip, "Name")
        sample = find_val(clip, ".//SampleRef/FileRef/Name")
        label = clip_name if clip_name else sample if sample else "(unnamed)"
        if sample and sample != label:
            label += f" [{sample}]"
        audio_clips.append(label)

    return {
        "type": track_type,
        "name": name,
        "devices": devices,
        "midi_clips": midi_clips,
        "audio_clips": audio_clips,
    }


def parse_als(path: str) -> None:
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with gzip.open(p, "rb") as f:
        tree = ET.parse(f)

    root = tree.getroot()  # <Ableton>
    minor_version = root.get("MinorVersion", "unknown")
    live_version = minor_version.split("_")[0] if "_" in minor_version else minor_version

    live_set = root.find("LiveSet")
    if live_set is None:
        print("Error: no LiveSet element found", file=sys.stderr)
        sys.exit(1)

    tempo = find_val(live_set, "Tempo/Manual")
    tsig_el = live_set.find(
        ".//TimeSignatures/RemoteableTimeSignature"
    )
    numerator = find_val(tsig_el, "Numerator") if tsig_el is not None else ""
    denominator = find_val(tsig_el, "Denominator") if tsig_el is not None else ""
    time_sig = f"{numerator}/{denominator}" if numerator and denominator else "unknown"

    # Scale awareness key (Live 11+)
    scale_root = find_val(live_set, ".//ScaleInformation/RootNote")
    scale_name = find_val(live_set, ".//ScaleInformation/Name")
    key_info = ""
    if scale_root or scale_name:
        key_info = f"{scale_root} {scale_name}".strip()

    tracks_el = live_set.find("Tracks")
    tracks = []
    if tracks_el is not None:
        for track_el in tracks_el:
            if track_el.tag in ("MidiTrack", "AudioTrack", "GroupTrack", "ReturnTrack"):
                tracks.append(parse_track(track_el))

    # Print summary
    print(f"Ableton Live {live_version}")
    print(f"File: {p.name}")
    print(f"Tempo: {tempo} BPM  |  Time signature: {time_sig}", end="")
    if key_info:
        print(f"  |  Key: {key_info}", end="")
    print()
    print()

    type_order = ["MidiTrack", "AudioTrack", "GroupTrack", "ReturnTrack"]
    for ttype in type_order:
        group = [t for t in tracks if t["type"] == ttype]
        if not group:
            continue
        label = ttype.replace("Track", "").upper()
        print(f"── {label} TRACKS ({'─' * (40 - len(label))})")
        for t in group:
            name = t["name"] if t["name"] else "(unnamed)"
            print(f"  {name}")
            if t["devices"]:
                for d in t["devices"]:
                    print(f"    {d}")
            if t["midi_clips"]:
                print(f"    Clips:")
                for c in t["midi_clips"]:
                    print(f"      • {c}")
            if t["audio_clips"]:
                print(f"    Clips:")
                for c in t["audio_clips"]:
                    print(f"      • {c}")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_als.py <path/to/project.als>", file=sys.stderr)
        sys.exit(1)
    parse_als(sys.argv[1])
