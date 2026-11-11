# AFRetextures

DayZ retextures for Allied Forces.

## Flags

| Class name | Texture |
| --- | --- |
| `Flag_AF_Cummins` | `AFRetextures/flags/data/flag_af_cummins_co.paa` |

The artwork is an original illustration. The editable master is
`source/flag_af_cummins.svg` (3:2). The texture is that image squashed to
1024x1024, on the assumption that the flag mesh stretches the full square back
out to flag proportions; `flag_af_cummins_co.png` is the same image for preview.

## Installing

`@AFRetextures` is a ready-to-load mod folder. Copy it to the server and to
clients, add `-mod=@AFRetextures`, and add `Flag_AF_Cummins` to the server's
`types.xml` (or spawn it by class name).

The PBO is unsigned, so it only loads where signature checks are off
(`verifySignatures = 0`). To sign it, or if the game rejects the PBO or the
texture, rebuild with DayZ Tools: pack the `AFRetextures` folder with Addon
Builder (prefix `AFRetextures`) and re-export `flag_af_cummins_co.png` with
ImageToPAA.

## Rebuilding

    python3 tools/mkpaa.py <rendered 3:2 png> AFRetextures/flags/data/flag_af_cummins_co.paa 1024
    python3 tools/mkpbo.py AFRetextures AFRetextures @AFRetextures/addons/AFRetextures.pbo
