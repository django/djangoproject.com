# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=500)),
                ('title', models.CharField(max_length=500)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentRelease',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lang', models.CharField(default='en', max_length=2, choices=[
                    ('af', 'Afrikaans'), ('ar', 'Arabic'),
                    ('ast', 'Asturian'), ('az', 'Azerbaijani'),
                    ('bg', 'Bulgarian'), ('be', 'Belarusian'),
                    ('bn', 'Bengali'), ('br', 'Breton'),
                    ('bs', 'Bosnian'), ('ca', 'Catalan'),
                    ('cs', 'Czech'), ('cy', 'Welsh'),
                    ('da', 'Danish'), ('de', 'German'),
                    ('el', 'Greek'), ('en', 'English'),
                    ('en-au', 'Australian English'),
                    ('en-gb', 'British English'),
                    ('eo', 'Esperanto'), ('es', 'Spanish'),
                    ('es-ar', 'Argentinian Spanish'),
                    ('es-mx', 'Mexican Spanish'),
                    ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'),
                    ('et', 'Estonian'), ('eu', 'Basque'),
                    ('fa', 'Persian'), ('fi', 'Finnish'),
                    ('fr', 'French'), ('fy', 'Frisian'),
                    ('ga', 'Irish'), ('gl', 'Galician'),
                    ('he', 'Hebrew'), ('hi', 'Hindi'),
                    ('hr', 'Croatian'), ('hu', 'Hungarian'),
                    ('ia', 'Interlingua'), ('id', 'Indonesian'),
                    ('io', 'Ido'), ('is', 'Icelandic'),
                    ('it', 'Italian'), ('ja', 'Japanese'),
                    ('ka', 'Georgian'), ('kk', 'Kazakh'),
                    ('km', 'Khmer'), ('kn', 'Kannada'),
                    ('ko', 'Korean'), ('lb', 'Luxembourgish'),
                    ('lt', 'Lithuanian'), ('lv', 'Latvian'),
                    ('mk', 'Macedonian'), ('ml', 'Malayalam'),
                    ('mn', 'Mongolian'), ('mr', 'Marathi'),
                    ('my', 'Burmese'), ('nb', 'Norwegian Bokmal'),
                    ('ne', 'Nepali'), ('nl', 'Dutch'),
                    ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'),
                    ('pa', 'Punjabi'), ('pl', 'Polish'),
                    ('pt', 'Portuguese'),
                    ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'),
                    ('ru', 'Russian'), ('sk', 'Slovak'),
                    ('sl', 'Slovenian'), ('sq', 'Albanian'),
                    ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'),
                    ('sv', 'Swedish'), ('sw', 'Swahili'),
                    ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'),
                    ('tr', 'Turkish'), ('tt', 'Tatar'),
                    ('udm', 'Udmurt'), ('uk', 'Ukrainian'),
                    ('ur', 'Urdu'), ('vi', 'Vietnamese'),
                    ('zh-cn', 'Simplified Chinese'),
                    ('zh-hans', 'Simplified Chinese'),
                    ('zh-hant', 'Traditional Chinese'),
                    ('zh-tw', 'Traditional Chinese'),
                ])),
                ('version', models.CharField(max_length=20)),
                ('scm', models.CharField(max_length=10, choices=[('svn', 'SVN'), ('git', 'git')])),
                ('scm_url', models.CharField(max_length=200)),
                ('docs_subdir', models.CharField(max_length=200, blank=True)),
                ('is_default', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='documentrelease',
            unique_together=set([('lang', 'version')]),
        ),
        migrations.AddField(
            model_name='document',
            name='release',
            field=models.ForeignKey(related_name='documents', to='docs.DocumentRelease'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set([('release', 'path')]),
        ),
    ]
