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
                    (b'af', b'Afrikaans'), (b'ar', b'Arabic'),
                    (b'ast', b'Asturian'), (b'az', b'Azerbaijani'),
                    (b'bg', b'Bulgarian'), (b'be', b'Belarusian'),
                    (b'bn', b'Bengali'), (b'br', b'Breton'),
                    (b'bs', b'Bosnian'), (b'ca', b'Catalan'),
                    (b'cs', b'Czech'), (b'cy', b'Welsh'),
                    (b'da', b'Danish'), (b'de', b'German'),
                    (b'el', b'Greek'), (b'en', b'English'),
                    (b'en-au', b'Australian English'),
                    (b'en-gb', b'British English'),
                    (b'eo', b'Esperanto'), (b'es', b'Spanish'),
                    (b'es-ar', b'Argentinian Spanish'),
                    (b'es-mx', b'Mexican Spanish'),
                    (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'),
                    (b'et', b'Estonian'), (b'eu', b'Basque'),
                    (b'fa', b'Persian'), (b'fi', b'Finnish'),
                    (b'fr', b'French'), (b'fy', b'Frisian'),
                    (b'ga', b'Irish'), (b'gl', b'Galician'),
                    (b'he', b'Hebrew'), (b'hi', b'Hindi'),
                    (b'hr', b'Croatian'), (b'hu', b'Hungarian'),
                    (b'ia', b'Interlingua'), (b'id', b'Indonesian'),
                    (b'io', b'Ido'), (b'is', b'Icelandic'),
                    (b'it', b'Italian'), (b'ja', b'Japanese'),
                    (b'ka', b'Georgian'), (b'kk', b'Kazakh'),
                    (b'km', b'Khmer'), (b'kn', b'Kannada'),
                    (b'ko', b'Korean'), (b'lb', b'Luxembourgish'),
                    (b'lt', b'Lithuanian'), (b'lv', b'Latvian'),
                    (b'mk', b'Macedonian'), (b'ml', b'Malayalam'),
                    (b'mn', b'Mongolian'), (b'mr', b'Marathi'),
                    (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'),
                    (b'ne', b'Nepali'), (b'nl', b'Dutch'),
                    (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'),
                    (b'pa', b'Punjabi'), (b'pl', b'Polish'),
                    (b'pt', b'Portuguese'),
                    (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'),
                    (b'ru', b'Russian'), (b'sk', b'Slovak'),
                    (b'sl', b'Slovenian'), (b'sq', b'Albanian'),
                    (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'),
                    (b'sv', b'Swedish'), (b'sw', b'Swahili'),
                    (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'),
                    (b'tr', b'Turkish'), (b'tt', b'Tatar'),
                    (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'),
                    (b'ur', b'Urdu'), (b'vi', b'Vietnamese'),
                    (b'zh-cn', b'Simplified Chinese'),
                    (b'zh-hans', b'Simplified Chinese'),
                    (b'zh-hant', b'Traditional Chinese'),
                    (b'zh-tw', b'Traditional Chinese'),
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
