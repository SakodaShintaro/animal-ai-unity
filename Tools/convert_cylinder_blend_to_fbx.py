# SPDX-License-Identifier: MIT
"""Convert Assets/Materials/Prefabs/Cylinder.blend to Cylinder.fbx.

`Cylinder.blend` was the only .blend in the project, and Unity imports a .blend
by shelling out to a Blender installation. On a machine without Blender the
import yields an empty mesh -- no error, but `CylinderTunnel` and
`CylinderTunnelTransparent` then spawn with no renderer geometry and no
collider, so both tunnels are silently absent from the built player. Every other
prefab's mesh comes from .fbx, which Unity reads on its own.

This script produces that .fbx once so the project no longer needs Blender to
build. It still needs Blender to RUN, which is what `uv run --with bpy` supplies
without installing anything system-wide:

    uv run --no-project --python 3.11 --with bpy==4.2.0 \
        python Tools/convert_cylinder_blend_to_fbx.py

The output is checked in beside the .blend; re-run it only if Cylinder.blend
changes. Cylinder.fbx.meta carries `useFileScale: 0` / `globalScale: 1`, which is
what puts the mesh at 2.08 x 2.08 x 2.00 -- exactly the reciprocal of the tunnel
prefabs' `ratioSize`, so a tunnel comes out the size its yaml asked for.
"""

import sys
from pathlib import Path

import bpy

SRC = Path("Assets/Materials/Prefabs/Cylinder.blend")
DST = Path("Assets/Materials/Prefabs/Cylinder.fbx")


def main() -> None:
    project = Path(__file__).resolve().parent.parent
    src, dst = project / SRC, project / DST
    assert src.exists(), f"{src} not found; run this from the Unity project"

    bpy.ops.wm.open_mainfile(filepath=str(src))
    # The .blend carries Blender's default Camera and Lamp beside the mesh;
    # Unity's own import produced a RootNode with all three, but only the mesh
    # is referenced by the prefabs.
    for obj in list(bpy.data.objects):
        if obj.type != "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)
    meshes = [(o.name, o.data.name, tuple(round(v, 4) for v in o.dimensions)) for o in bpy.data.objects]
    assert len(meshes) == 1, f"expected one mesh, got {meshes}"
    print(f"exporting {meshes[0]}")

    # Blender's FBX defaults (-Z forward, Y up) put the tube's axis on Unity's
    # z and its cross-section on x/y, which is the orientation the prefabs'
    # ratioSize (1/2.08, 1/2.08, 1/2.0) was tuned against.
    bpy.ops.export_scene.fbx(
        filepath=str(dst),
        use_selection=False,
        apply_unit_scale=True,
        axis_forward="-Z",
        axis_up="Y",
        object_types={"MESH"},
        mesh_smooth_type="FACE",
    )
    print(f"wrote {dst}")


if __name__ == "__main__":
    sys.exit(main())
