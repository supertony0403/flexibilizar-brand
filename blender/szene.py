"""Blender scene: the strip feeds out of a recorder, folds three times into the F, the name types out.

    blender -b --factory-startup --python blender/szene.py -- intro AUSGABE [--von N --bis N --schritt N --prozent P --samples S]

Frames are rendered one by one with the fold written straight into the mesh (see the notes on
render(animation=True) in the project memory). The fold itself lives in marke/falz.py.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from marke.falz import BANNER, Masse, falten, gitter, laenge_gesamt  # noqa: E402
from marke.spur import spur  # noqa: E402

ARBEIT = Path("/mnt/steam-library/flexibilizar/arbeit")
FPS = 24
LETZTES_BILD = 132
SHUTTER = 0.5  # 180-degree shutter, in frames

M = Masse()
LAGE = 0.022  # layer distance, large enough to clear the sheet's own ripple
FEDER_X = -7.25  # pen position, just right of the strip's tail end


def glatt(a: float, b: float, x: float) -> float:
    """Smootherstep from 0 at a to 1 at b."""
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * t * (t * (t * 6 - 15) + 10)


def aus(a: float, b: float, x: float, p: float = 3.0) -> float:
    """Ease-out, fast start, soft landing."""
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return 1 - (1 - t) ** p


def schnapp(a: float, b: float, x: float) -> float:
    """Fold motion: a slow lift, a fast slap, pressed flat at the end."""
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t**2.6 * (3 - 2 * t)


# Fold windows in frames. Overlap a little, so each fold lifts while the previous one lands.
# The landings sit on the stinger's beat (2.021, 2.449 and 2.878 s), keep ton/mischen.py in step.
FENSTER = ((36.0, 49.5), (46.5, 59.78), (56.5, 70.08))
SCHREIB_START, SCHREIB_JE = 72, 2


def falzwinkel(f: float) -> tuple[float, float, float]:
    return tuple(math.pi * schnapp(a, b, f) for a, b in FENSTER)


def falzradius(f: float) -> tuple[float, float, float]:
    """Round while moving, pressed sharp as the fold lands."""
    return tuple(0.34 * (1 - glatt(b - 4, b + 1, f)) + 0.012 for _, b in FENSTER)


def vorschub(f: float) -> float:
    """Strip offset along x. Zero is its final place. The tail leaves the pen at about frame 32."""
    return -11.2 * (1 - aus(1, 34, f, 2.4))


def blatt_gitter(m: Masse = M, dichte: int = 58) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Flat grid of the unfolded strip: vertices, quad indices, uv."""
    laenge = laenge_gesamt(m)
    rechts = 1 + m.arm_oben
    x, vv = gitter(m, dichte)
    nu, nv = x.shape[0] - 1, x.shape[1] - 1
    uu = (x - (rechts - laenge)) / laenge
    y = m.hoehe - 1 + vv
    # Paper is never perfectly flat: a low swell, and the free ends lift a touch.
    z = (
        0.006 * np.sin(x * 2.1 + y * 1.3)
        + 0.004 * np.sin(x * 5.3 - y * 3.1 + 1.0)
        + 0.03 * np.clip(1 - (rechts - x) / 0.5, 0, 1) ** 2
        + 0.012 * np.clip(1 - (x - (rechts - laenge)) / 0.5, 0, 1) ** 2
    )
    punkte = np.c_[x.ravel(), y.ravel(), z.ravel()]
    i = np.arange((nu + 1) * (nv + 1)).reshape(nu + 1, nv + 1)
    quads = np.c_[i[:-1, :-1].ravel(), i[1:, :-1].ravel(), i[1:, 1:].ravel(), i[:-1, 1:].ravel()]
    return punkte, quads, np.c_[uu.ravel(), vv.ravel()]


def bild(name: str, farbdaten: bool = True) -> bpy.types.Image:
    b = bpy.data.images.load(str(ARBEIT / name))
    b.colorspace_settings.name = "sRGB" if farbdaten else "Non-Color"
    return b


def papier_material(vorn_bild: str = "streifen_vorn.png") -> tuple[bpy.types.Material, bpy.types.Node]:
    """Two-sided paper: chart grid and trace on the front, marker on the back, a little translucent."""
    mat = bpy.data.materials.new("Papier")
    mat.use_nodes = True
    k, n = mat.node_tree.nodes, mat.node_tree.links
    k.clear()
    ausgang = k.new("ShaderNodeOutputMaterial")
    uv = k.new("ShaderNodeTexCoord")
    vorn = k.new("ShaderNodeTexImage")
    vorn.image = bild(vorn_bild)
    hinten = k.new("ShaderNodeTexImage")
    hinten.image = bild("streifen_hinten.png")
    spur = k.new("ShaderNodeTexImage")
    spur.image = bild("streifen_spur.png", False)
    for t in (vorn, hinten, spur):
        n.new(uv.outputs["UV"], t.inputs["Vector"])

    # Reveal: ink exists only for u greater than the pen's current position on the strip.
    sep = k.new("ShaderNodeSeparateXYZ")
    n.new(uv.outputs["UV"], sep.inputs[0])
    feder = k.new("ShaderNodeValue")
    feder.name = "FederU"
    groesser = k.new("ShaderNodeMath")
    groesser.operation = "GREATER_THAN"
    n.new(sep.outputs["X"], groesser.inputs[0])
    n.new(feder.outputs[0], groesser.inputs[1])
    mal = k.new("ShaderNodeMath")
    mal.operation = "MULTIPLY"
    n.new(spur.outputs["Color"], mal.inputs[0])
    n.new(groesser.outputs[0], mal.inputs[1])
    tinte = k.new("ShaderNodeMix")
    tinte.data_type = "RGBA"
    n.new(mal.outputs[0], tinte.inputs[0])
    n.new(vorn.outputs["Color"], tinte.inputs[6])
    tinte.inputs[7].default_value = (0.012, 0.009, 0.007, 1)

    geo = k.new("ShaderNodeNewGeometry")
    seite = k.new("ShaderNodeMix")
    seite.data_type = "RGBA"
    n.new(geo.outputs["Backfacing"], seite.inputs[0])
    n.new(tinte.outputs[2], seite.inputs[6])
    n.new(hinten.outputs["Color"], seite.inputs[7])

    prin = k.new("ShaderNodeBsdfPrincipled")
    n.new(seite.outputs[2], prin.inputs["Base Color"])
    prin.inputs["Roughness"].default_value = 0.78
    prin.inputs["Specular IOR Level"].default_value = 0.25
    durch = k.new("ShaderNodeBsdfTranslucent")
    n.new(seite.outputs[2], durch.inputs["Color"])
    mix = k.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.12
    n.new(prin.outputs[0], mix.inputs[1])
    n.new(durch.outputs[0], mix.inputs[2])
    n.new(mix.outputs[0], ausgang.inputs["Surface"])
    return mat, feder


def tisch_material() -> bpy.types.Material:
    """Dark bookbinding cloth: warm near-black, a fine grain instead of a weave (which moires)."""
    mat = bpy.data.materials.new("Tisch")
    mat.use_nodes = True
    k, n = mat.node_tree.nodes, mat.node_tree.links
    prin = k["Principled BSDF"]
    co = k.new("ShaderNodeTexCoord")
    mp = k.new("ShaderNodeMapping")
    n.new(co.outputs["Object"], mp.inputs["Vector"])
    korn = k.new("ShaderNodeTexNoise")
    korn.inputs["Scale"].default_value = 210
    korn.inputs["Detail"].default_value = 3.0
    n.new(mp.outputs[0], korn.inputs["Vector"])
    rausch = k.new("ShaderNodeTexNoise")
    rausch.inputs["Scale"].default_value = 3.0
    rausch.inputs["Detail"].default_value = 8.0
    n.new(mp.outputs[0], rausch.inputs["Vector"])
    ramp = k.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0.0042, 0.0034, 0.0027, 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.0105, 0.0085, 0.0066, 1)
    n.new(rausch.outputs[0], ramp.inputs["Fac"])
    n.new(ramp.outputs[0], prin.inputs["Base Color"])
    prin.inputs["Roughness"].default_value = 0.8
    prin.inputs["Specular IOR Level"].default_value = 0.12
    bump = k.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    bump.inputs["Distance"].default_value = 0.02
    n.new(korn.outputs["Fac"], bump.inputs["Height"])
    n.new(bump.outputs[0], prin.inputs["Normal"])
    return mat


def wort_material() -> tuple[bpy.types.Material, bpy.types.Node]:
    """Name printed on the cloth, with a hard letter-by-letter reveal."""
    mat = bpy.data.materials.new("Wort")
    mat.use_nodes = True
    k, n = mat.node_tree.nodes, mat.node_tree.links
    prin = k["Principled BSDF"]
    prin.inputs["Base Color"].default_value = (0.86, 0.79, 0.68, 1)
    prin.inputs["Roughness"].default_value = 0.72
    prin.inputs["Specular IOR Level"].default_value = 0.2
    co = k.new("ShaderNodeTexCoord")
    tex = k.new("ShaderNodeTexImage")
    tex.image = bild("wortmarke.png", False)
    tex.extension = "CLIP"  # wrapping would print the letters' feet along the plane's top edge
    n.new(co.outputs["UV"], tex.inputs["Vector"])
    sep = k.new("ShaderNodeSeparateXYZ")
    n.new(co.outputs["UV"], sep.inputs[0])
    grenze = k.new("ShaderNodeValue")
    grenze.name = "WortU"
    kleiner = k.new("ShaderNodeMath")
    kleiner.operation = "LESS_THAN"
    n.new(sep.outputs["X"], kleiner.inputs[0])
    n.new(grenze.outputs[0], kleiner.inputs[1])
    mal = k.new("ShaderNodeMath")
    mal.operation = "MULTIPLY"
    n.new(tex.outputs["Color"], mal.inputs[0])
    n.new(kleiner.outputs[0], mal.inputs[1])
    n.new(mal.outputs[0], prin.inputs["Alpha"])
    return mat, grenze


def feder_bauen() -> tuple[bpy.types.Object, bpy.types.Object]:
    """Recorder pen: a thin brass arm with a dark tip, built along +X from its hinge at the origin."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.011, depth=1, rotation=(0, math.pi / 2, 0), location=(0.5, 0, 0))
    arm = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mat = bpy.data.materials.new("Messing")
    mat.use_nodes = True
    prin = mat.node_tree.nodes["Principled BSDF"]
    prin.inputs["Base Color"].default_value = (0.42, 0.30, 0.15, 1)
    prin.inputs["Metallic"].default_value = 1.0
    prin.inputs["Roughness"].default_value = 0.32
    arm.data.materials.append(mat)
    arm.name = "Feder"
    # Ink tip: a little dark cone standing on the paper.
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.0, radius2=0.05, depth=0.17, location=(0, 0, 0.085))
    kopf = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    kopf.location = (0, 0, 0)
    dunkel = bpy.data.materials.new("Spitze")
    dunkel.use_nodes = True
    p = dunkel.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.02, 0.018, 0.016, 1)
    p.inputs["Roughness"].default_value = 0.3
    kopf.data.materials.append(dunkel)
    kopf.name = "Kopf"
    return arm, kopf


def licht_und_welt() -> None:
    welt = bpy.data.worlds.new("Raum")
    welt.use_nodes = True
    welt.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.48, 0.40, 1)
    welt.node_tree.nodes["Background"].inputs[1].default_value = 0.035
    bpy.context.scene.world = welt
    # Key: a long warm window, raking from the upper left. Everything lives off its shadows.
    bpy.ops.object.light_add(type="AREA", location=(-5.0, 22.0, 17.0))
    lampe = bpy.context.object
    lampe.data.shape = "RECTANGLE"
    lampe.data.size, lampe.data.size_y = 14.0, 5.0
    lampe.data.energy = 9800
    lampe.data.color = (1.0, 0.88, 0.72)
    richtung = Vector((2.0, 1.5, 0)) - lampe.location
    lampe.rotation_euler = richtung.to_track_quat("-Z", "Y").to_euler()
    # Fill from above, far weaker, so the shadow side of a fold stays paper and not black.
    bpy.ops.object.light_add(type="AREA", location=(3.0, 2.0, 16.0))
    fuell = bpy.context.object
    fuell.data.size = 18.0
    fuell.data.energy = 360
    fuell.data.color = (1.0, 0.95, 0.88)


def kamera_bauen() -> bpy.types.Object:
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    bpy.context.scene.camera = cam
    cam.data.sensor_width = 36
    cam.data.dof.use_dof = True
    return cam


# Camera poses: frame, position, target, lens, f-stop. Starts as a macro on the pen.
POSEN = (
    (1, (-5.7, 1.5, 2.1), (-6.25, 4.05, 0), 38, 2.0),
    (16, (-5.3, 0.1, 3.5), (-5.0, 4.05, 0), 36, 2.4),
    (34, (-2.1, -2.8, 7.0), (-2.1, 4.0, 0), 34, 4.0),
    (50, (1.6, -1.0, 12.5), (1.6, 3.0, 0), 42, 8.0),
    (76, (4.55, 2.14, 18.2), (4.55, 2.16, 0), 50, 11.0),
    (133, (4.55, 2.14, 17.75), (4.55, 2.16, 0), 50, 11.0),
)


def _catmull(p0: Vector, p1: Vector, p2: Vector, p3: Vector, t: float) -> Vector:
    return 0.5 * (
        2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2 + (3 * p1 - p0 - 3 * p2 + p3) * t**3
    )


def kamera_pose(f: float) -> tuple[Vector, Vector, float, float, float]:
    """Position, target, lens, f-stop, roll in degrees at frame f, a spline through POSEN."""
    f = max(POSEN[0][0], min(POSEN[-1][0] - 1e-3, f))
    i = next(i for i in range(len(POSEN) - 1) if POSEN[i][0] <= f < POSEN[i + 1][0])
    a, b = POSEN[i], POSEN[i + 1]
    v, n = POSEN[max(i - 1, 0)], POSEN[min(i + 2, len(POSEN) - 1)]
    t = (f - a[0]) / (b[0] - a[0])
    pos = _catmull(*(Vector(q[1]) for q in (v, a, b, n)), t)
    ziel = _catmull(*(Vector(q[2]) for q in (v, a, b, n)), t)
    glatt_t = t * t * (3 - 2 * t)
    return pos, ziel, a[3] + (b[3] - a[3]) * glatt_t, a[4] + (b[4] - a[4]) * glatt_t, -3.4 * (1 - glatt(30, 66, f))


def kamera_setzen(cam: bpy.types.Object, f: float) -> None:
    pos, ziel, lens, blende, roll = kamera_pose(f)
    cam.location = pos
    blick = ziel - pos
    # Built by hand: to_track_quat is free to spin the image when looking straight down.
    vorn = blick.normalized()
    rechts = vorn.cross(Vector((0, 1, 0))).normalized()
    oben = rechts.cross(vorn)
    cam.rotation_euler = Matrix((rechts, oben, -vorn)).transposed().to_euler()
    cam.rotation_euler.rotate_axis("Z", math.radians(roll))
    cam.data.lens = lens
    cam.data.dof.focus_distance = blick.length
    cam.data.dof.aperture_fstop = blende


def feder_setzen(arm: bpy.types.Object, kopf: bpy.types.Object, f: float, y_spur: np.ndarray, laenge: float) -> None:
    """Point the arm from its hinge (above the frame) at the pen tip riding the trace."""
    links = 1 + M.arm_oben - laenge
    u = (FEDER_X - vorschub(f) - links) / laenge
    lift = glatt(29, 37, f)
    i = int(max(0.0, min(1.0, u)) * (len(y_spur) - 1))
    spitze = Vector((FEDER_X, M.hoehe - 0.5 + y_spur[i] * 0.36, 0.06 + 0.03 * lift))
    spitze += Vector((-1.6, 12.0, 4.0)) * lift
    gelenk = Vector((FEDER_X - 1.6, 16.5, 3.4))
    d = spitze - gelenk
    arm.location = gelenk
    arm.rotation_euler = d.to_track_quat("X", "Z").to_euler()
    arm.scale = (d.length, 1, 1)
    kopf.location = spitze


def alle_keys(cam, arm, kopf, y_spur, laenge) -> None:
    """Key camera and pen at both shutter ends of every frame, so Cycles can blur them."""
    for f in range(1, LETZTES_BILD + 1):
        for t in (f - SHUTTER / 2, f + SHUTTER / 2):
            kamera_setzen(cam, t)
            feder_setzen(arm, kopf, t, y_spur, laenge)
            cam.keyframe_insert("location", frame=t)
            cam.keyframe_insert("rotation_euler", frame=t)
            cam.data.keyframe_insert("lens", frame=t)
            cam.data.dof.keyframe_insert("focus_distance", frame=t)
            cam.data.dof.keyframe_insert("aperture_fstop", frame=t)
            for ob, attrs in ((arm, ("location", "rotation_euler", "scale")), (kopf, ("location",))):
                for at in attrs:
                    ob.keyframe_insert(at, frame=t)


def cycles_einrichten(szene: bpy.types.Scene, samples: int, gpu: bool) -> None:
    szene.render.engine = "CYCLES"
    c = szene.cycles
    c.samples = samples
    c.use_denoising = True
    c.denoiser = "OPENIMAGEDENOISE"
    c.max_bounces = 5
    c.caustics_reflective = c.caustics_refractive = False
    c.device = "CPU"
    if gpu:
        pr = bpy.context.preferences.addons["cycles"].preferences
        pr.compute_device_type = "ONEAPI"
        pr.use_oneapirt = False  # the level-zero raytracing library is not installed
        pr.get_devices()
        for d in pr.devices:
            d.use = d.type == "ONEAPI"
        if any(d.use for d in pr.devices):
            c.device = "GPU"
    print("Cycles-Gerät:", c.device, flush=True)


def szene_grund(prozent: int, samples: int, gpu: bool, b: int = 1920, h: int = 1080) -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.resolution_x, s.render.resolution_y = b, h
    s.render.resolution_percentage = prozent
    s.render.fps = FPS
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.compression = 40
    s.view_settings.view_transform = "Standard"
    s.view_settings.look = "None"
    s.view_settings.exposure = 0.0
    cycles_einrichten(s, samples, gpu)
    return s


def tisch_bauen() -> None:
    bpy.ops.mesh.primitive_plane_add(size=90, location=(0, 2, -0.03))
    bpy.context.object.data.materials.append(tisch_material())


def streifen_bauen(s: bpy.types.Scene, flach, quads, uv, material: bpy.types.Material):
    me = bpy.data.meshes.new("Streifen")
    me.from_pydata(flach.tolist(), [], quads.tolist())
    me.update()
    me.uv_layers.new(name="UV")
    schleifen = np.array([li.vertex_index for li in me.loops])
    me.uv_layers[0].data.foreach_set("uv", uv[schleifen].ravel())
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    streifen = bpy.data.objects.new("Streifen", me)
    s.collection.objects.link(streifen)
    me.materials.append(material)
    return streifen, me


def banner(args: argparse.Namespace) -> None:
    """Still: the F's top arm as a 380 px band across the frame, shot straight down, orthographic."""
    b, h, je_einheit = 2560, 1440, 380.0
    links_px = 129.0  # stem's left edge, chosen so the fold's triangle ends at the safe zone
    s = szene_grund(args.prozent, args.samples, not args.cpu, b, h)
    tisch_bauen()
    licht_und_welt()
    flach, quads, uv = blatt_gitter(BANNER, 40)
    pm, feder_u = papier_material("banner_vorn.png")
    feder_u.outputs[0].default_value = 2.0  # the trace is printed into this texture
    _, me = streifen_bauen(s, flach, quads, uv, pm)
    p = falten(flach, BANNER, (math.pi, math.pi, math.pi), 0.012, LAGE)
    me.vertices.foreach_set("co", p.ravel())
    me.update()
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    s.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = b / je_einheit
    # Band centred on the frame, as the safe zone demands.
    cam.location = ((b / 2 - links_px) / je_einheit, BANNER.hoehe - 0.5, 20.0)
    cam.rotation_euler = (0, 0, 0)
    Path(args.ausgabe).parent.mkdir(parents=True, exist_ok=True)
    s.render.filepath = args.ausgabe
    bpy.ops.render.render(write_still=True)


def avatar(args: argparse.Namespace) -> None:
    """The mark alone as a paper object, for the round avatar."""
    s = szene_grund(args.prozent, args.samples, not args.cpu, 800, 800)
    tisch_bauen()
    licht_und_welt()
    flach, quads, uv = blatt_gitter(M, 58)
    pm, feder_u = papier_material()
    feder_u.outputs[0].default_value = 2.0  # no trace: at 48 px it is only noise
    _, me = streifen_bauen(s, flach, quads, uv, pm)
    me.vertices.foreach_set("co", falten(flach, M, (math.pi,) * 3, 0.012, LAGE).ravel())
    me.update()
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    s.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 800 / 134  # same scale as the vector version
    cam.location = (M.breite / 2 - 0.03, M.hoehe / 2, 20.0)
    cam.rotation_euler = (0, 0, 0)
    s.render.filepath = args.ausgabe
    bpy.ops.render.render(write_still=True)


def intro(args: argparse.Namespace) -> None:
    s = szene_grund(args.prozent, args.samples, not args.cpu)
    tisch_bauen()
    licht_und_welt()
    cam = kamera_bauen()

    flach, quads, uv = blatt_gitter()
    pm, feder_u = papier_material()
    streifen, me = streifen_bauen(s, flach, quads, uv, pm)

    # Name in the empty space under the middle arm, baseline on the stem's foot.
    wort_x = 1.32
    wort_breite = 7.55
    wort_h = wort_breite * 400 / 3000
    bpy.ops.mesh.primitive_plane_add(size=1, location=(wort_x + wort_breite / 2, wort_h / 2, -0.018))
    wort = bpy.context.object
    wort.scale = (wort_breite, wort_h, 1)
    wm, wort_u = wort_material()
    wort.data.materials.append(wm)
    kanten = [float(z) for z in (ARBEIT / "wortmarke_kanten.txt").read_text().split()]

    laenge = laenge_gesamt(M)
    # Same signal the texture was drawn from, so the pen really rides the trace.
    y_spur = spur(round(laenge * 400))
    arm, kopf = feder_bauen()
    alle_keys(cam, arm, kopf, y_spur, laenge)

    # Deformation blur: two shape keys hold the sheet at both shutter ends of the current frame.
    streifen.shape_key_add(name="Basis")
    k_a = streifen.shape_key_add(name="A")
    k_b = streifen.shape_key_add(name="B")
    s.render.use_motion_blur = True
    s.render.motion_blur_shutter = SHUTTER
    s.render.motion_blur_position = "CENTER"

    ziel = Path(args.ausgabe)
    ziel.mkdir(parents=True, exist_ok=True)
    links = 1 + M.arm_oben - laenge
    bpy.context.view_layer.update()
    for f in range(args.von, args.bis + 1, args.schritt):
        for t, key in ((f - SHUTTER / 2, k_a), (f + SHUTTER / 2, k_b)):
            p = falten(flach, M, falzwinkel(t), falzradius(t), LAGE)
            p[:, 0] += vorschub(t)
            key.data.foreach_set("co", p.ravel())
        for key, von_w, bis_w in ((k_a, 1.0, 0.0), (k_b, 0.0, 1.0)):
            if me.shape_keys.animation_data:
                me.shape_keys.animation_data_clear()
        for key, von_w, bis_w in ((k_a, 1.0, 0.0), (k_b, 0.0, 1.0)):
            key.value = von_w
            key.keyframe_insert("value", frame=f - SHUTTER / 2)
            key.value = bis_w
            key.keyframe_insert("value", frame=f + SHUTTER / 2)
        off = vorschub(f)
        feder_u.outputs[0].default_value = (FEDER_X - off - links) / laenge
        n = (f - SCHREIB_START) // SCHREIB_JE + 1
        wort_u.outputs[0].default_value = 0.0 if n <= 0 else (1.01 if n >= len(kanten) else kanten[n - 1])
        arm.hide_render = kopf.hide_render = f > 38
        s.frame_set(f)
        bpy.context.view_layer.update()
        s.render.filepath = str(ziel / f"f{f:04d}.png")
        if args.neu or not Path(s.render.filepath).exists():
            bpy.ops.render.render(write_still=True)
            print(f"BILD {f}", flush=True)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :]
    a = argparse.ArgumentParser()
    a.add_argument("modus", choices=["intro", "banner", "avatar"])
    a.add_argument("ausgabe")
    a.add_argument("--von", type=int, default=1)
    a.add_argument("--bis", type=int, default=LETZTES_BILD)
    a.add_argument("--schritt", type=int, default=1)
    a.add_argument("--prozent", type=int, default=100)
    a.add_argument("--samples", type=int, default=48)
    a.add_argument("--cpu", action="store_true")
    a.add_argument("--neu", action="store_true")
    args = a.parse_args(argv)
    {"intro": intro, "banner": banner, "avatar": avatar}[args.modus](args)


if __name__ == "__main__":
    main()
