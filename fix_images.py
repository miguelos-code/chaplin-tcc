import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chaplin_project.settings')
django.setup()

from apps.tasks.models import TaskEvidence

mapping = {
    6: "evidences/lampada_queimada_corredor.png",
    7: "evidences/vazamento_banheiro_terreo.png",
    8: "evidences/rachadura_escadaria.png",
    9: "evidences/tomada_danificada_sala201.png",
    10: "evidences/filtro_ar_sujo_recepcao.png",
    11: "evidences/macaneta_nova_almoxarifado.png",
    12: "evidences/elevador_painel_reparado.png",
    13: "evidences/forro_novo_sala105.png",
    14: "evidences/pintura_desgastada_hall.png",
    15: "evidences/lampadas_led_garagem.png",
    16: "evidences/sistema_hidraulico_5andar.png",
    17: "evidences/rampa_sem_corrimao.png",
}

for task_id, photo_path in mapping.items():
    evidence = TaskEvidence.objects.filter(task_id=task_id).first()
    if evidence:
        evidence.photo = photo_path
        evidence.save()
        print(f"Updated task {task_id} to {photo_path}")
    else:
        print(f"Evidence for task {task_id} not found")
