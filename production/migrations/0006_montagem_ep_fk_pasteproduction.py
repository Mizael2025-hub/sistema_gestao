# Manual migration: vincula positive_ep / negative_ep da montagem (Assembly)
# a apontamentos de empaste (PasteProduction).
#
# Etapas:
# 1. Cria novos campos FK nullable (positive_ep_v2 / negative_ep_v2).
# 2. Migra dados antigos (CharField com o `lot` do empaste) para a FK nova.
# 3. Remove os campos CharField antigos.
# 4. Renomeia os novos FKs de volta para positive_ep / negative_ep.

from django.db import migrations, models
import django.db.models.deletion


def migrate_ep_forward(apps, schema_editor):
    Assembly = apps.get_model('production', 'Assembly')
    Paste = apps.get_model('production', 'PasteProduction')
    for asm in Assembly.objects.all():
        pos_lot = asm.positive_ep    # CharField antigo (texto)
        neg_lot = asm.negative_ep    # CharField antigo (texto)
        if pos_lot:
            paste = Paste.objects.filter(lot=pos_lot, polarity='POS').first() \
                or Paste.objects.filter(lot=pos_lot).first()
            if paste:
                asm.positive_ep_v2 = paste
        if neg_lot:
            paste = Paste.objects.filter(lot=neg_lot, polarity='NEG').first() \
                or Paste.objects.filter(lot=neg_lot).first()
            if paste:
                asm.negative_ep_v2 = paste
        asm.save()


def migrate_ep_backward(apps, schema_editor):
    # Não restaurável de forma confiável.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0005_masseira_renomeia_oxido_adicao'),
    ]

    operations = [
        # 1. Novos campos FK, nullable.
        migrations.AddField(
            model_name='assembly',
            name='positive_ep_v2',
            field=models.ForeignKey(
                blank=True,
                help_text='Empaste positivo utilizado (vinculado a um apontamento de empaste).',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='assemblies_positive',
                to='production.pasteproduction',
                verbose_name='EP positiva',
            ),
        ),
        migrations.AddField(
            model_name='assembly',
            name='negative_ep_v2',
            field=models.ForeignKey(
                blank=True,
                help_text='Empaste negativo utilizado (vinculado a um apontamento de empaste).',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='assemblies_negative',
                to='production.pasteproduction',
                verbose_name='EP negativa',
            ),
        ),

        # 2. Converter dados existentes (texto do lote -> FK).
        migrations.RunPython(migrate_ep_forward, migrate_ep_backward),

        # 3. Remover campos CharField antigos.
        migrations.RemoveField(model_name='assembly', name='positive_ep'),
        migrations.RemoveField(model_name='assembly', name='negative_ep'),

        # 4. Renomear novos FKs de volta aos nomes originais.
        migrations.RenameField(
            model_name='assembly', old_name='positive_ep_v2', new_name='positive_ep',
        ),
        migrations.RenameField(
            model_name='assembly', old_name='negative_ep_v2', new_name='negative_ep',
        ),
    ]