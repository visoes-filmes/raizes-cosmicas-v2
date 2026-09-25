# -*- coding: utf-8 -*-
"""Roda DENTRO do Unreal (commandlet pythonscript): le uma AnimSequence e
escreve as posicoes das juntas no espaco do componente, quadro a quadro, em
JSON. Raizes Cosmicas 7.1 -- a deusa que danca."""
import json
import os
import unreal

SAIDA = r"D:\_exportar_mocap_temp\mocap_praia.json"
CANDIDATOS = [
    "/Game/CampoDeGirassois/Personagem_Riggada/Anims/AS_PERF_PraiaC0094_Body_v5",
    "/Game/AS_PERF_PraiaC0094_Body",
    "/Game/CampoDeGirassois/Personagem_Riggada/Anims/A_Gabi_MocapPraia_v2",
]
FPS_SAIDA = 15.0

# as juntas que interessam, nos dois vocabularios (MetaHuman/manequim e Mixamo)
QUERIDAS = {
    "pelvis": ["pelvis", "mixamorig_Hips", "Hips", "hips"],
    "spine": ["spine_02", "mixamorig_Spine", "Spine", "spine_01"],
    "chest": ["spine_04", "mixamorig_Spine2", "Spine2", "spine_03", "spine_05"],
    "neck": ["neck_01", "mixamorig_Neck", "Neck", "neck_02"],
    "head": ["head", "mixamorig_Head", "Head"],
    "shoulder_l": ["clavicle_l", "mixamorig_LeftShoulder", "LeftShoulder"],
    "upperarm_l": ["upperarm_l", "mixamorig_LeftArm", "LeftArm"],
    "lowerarm_l": ["lowerarm_l", "mixamorig_LeftForeArm", "LeftForeArm"],
    "hand_l": ["hand_l", "mixamorig_LeftHand", "LeftHand"],
    "shoulder_r": ["clavicle_r", "mixamorig_RightShoulder", "RightShoulder"],
    "upperarm_r": ["upperarm_r", "mixamorig_RightArm", "RightArm"],
    "lowerarm_r": ["lowerarm_r", "mixamorig_RightForeArm", "RightForeArm"],
    "hand_r": ["hand_r", "mixamorig_RightHand", "RightHand"],
    "thigh_l": ["thigh_l", "mixamorig_LeftUpLeg", "LeftUpLeg"],
    "calf_l": ["calf_l", "mixamorig_LeftLeg", "LeftLeg"],
    "foot_l": ["foot_l", "mixamorig_LeftFoot", "LeftFoot"],
    "toe_l": ["ball_l", "mixamorig_LeftToeBase", "LeftToeBase"],
    "thigh_r": ["thigh_r", "mixamorig_RightUpLeg", "RightUpLeg"],
    "calf_r": ["calf_r", "mixamorig_RightLeg", "RightLeg"],
    "foot_r": ["foot_r", "mixamorig_RightFoot", "RightFoot"],
    "toe_r": ["ball_r", "mixamorig_RightToeBase", "RightToeBase"],
}


def log(m):
    unreal.log_warning("[mocap] " + str(m))


anim = None
for c in CANDIDATOS:
    a = unreal.load_asset(c)
    if a:
        anim = a
        log("carregada: " + c)
        break
    log("nao achei: " + c)
if not anim:
    raise SystemExit("nenhuma animacao encontrada")

n_quadros = unreal.AnimationLibrary.get_num_frames(anim)
taxa = unreal.AnimationLibrary.get_rate_scale(anim)
comp = anim.get_editor_property("sequence_length") if hasattr(anim, "get_editor_property") else 0
try:
    fr = unreal.AnimationLibrary.get_anim_sequence_frame_rate(anim)  # nem toda versao tem
    fps_anim = fr.numerator / max(1, fr.denominator)
except Exception:
    fps_anim = 30.0
log("quadros=%d duracao=%s fps=%s escala=%s" % (n_quadros, comp, fps_anim, taxa))

opcoes = unreal.AnimPoseEvaluationOptions()
try:
    opcoes.set_editor_property("evaluation_type", unreal.AnimDataEvalType.RAW)
except Exception:
    pass
try:
    opcoes.set_editor_property("extract_root_motion", False)
except Exception:
    pass

pose0 = unreal.AnimPoseExtensions.get_anim_pose_at_frame(anim, 0, opcoes)
nomes = [str(n) for n in unreal.AnimPoseExtensions.get_bone_names(pose0)]
log("ossos (%d): %s" % (len(nomes), " ".join(nomes[:80])))

escolha = {}
for chave, cands in QUERIDAS.items():
    for cnd in cands:
        if cnd in nomes:
            escolha[chave] = cnd
            break
log("juntas escolhidas: " + json.dumps(escolha))

# os pais, se a API der (tentativas; se nada der, fica vazio e o obra usa o mapa fixo)
pais = {}
for k, osso in escolha.items():
    try:
        p = unreal.AnimPoseExtensions.get_parent_bone_name(pose0, osso)
        pais[k] = str(p)
    except Exception:
        pass

passo = max(1, int(round(fps_anim / FPS_SAIDA)))
quadros = []
for f in range(0, n_quadros, passo):
    pose = unreal.AnimPoseExtensions.get_anim_pose_at_frame(anim, f, opcoes)
    linha = []
    for chave in QUERIDAS:
        osso = escolha.get(chave)
        if not osso:
            linha.extend([0, 0, 0])
            continue
        tr = unreal.AnimPoseExtensions.get_bone_pose(pose, osso, unreal.AnimPoseSpaces.WORLD)
        loc = tr.translation
        # Unreal e cm, Z para cima, X para a frente, Y para a direita (mao esquerda).
        # A obra e metros, Y para cima, -Z para a frente (mao direita): (x, y, z) -> (y, z, -x)/100
        linha.extend([round(loc.y / 100.0, 4), round(loc.z / 100.0, 4), round(-loc.x / 100.0, 4)])
    quadros.append(linha)
    if f % (passo * 150) == 0:
        log("quadro %d/%d" % (f, n_quadros))

dados = {
    "origem": anim.get_path_name(),
    "fps": fps_anim / passo,
    "juntas": list(QUERIDAS.keys()),
    "ossos": escolha,
    "pais": pais,
    "quadros": quadros,
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w", encoding="utf-8") as fh:
    json.dump(dados, fh)
log("escrito %s: %d quadros a %.2f fps" % (SAIDA, len(quadros), dados["fps"]))
