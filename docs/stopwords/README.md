# Instructions to create a new search dictionary

In this folder, there is `custom_english.stop`.

This copies the [snowball english stop words](https://github.com/postgres/postgres/blob/master/src/backend/snowball/stopwords/english.stop)
but removes some stop words such as "through" and "when". This is because these
terms are also used in Django code.

The file format is a list of words, one per line. Blank lines and trailing
spaces are ignored, and upper case is folded to lower case, but no other
processing is done on the file contents.

This file needs to be created in `$SHAREDIR/tsearch_data/custom_english.stop`,
where `$SHAREDIR` means the PostgreSQL installation's shared-data directory,
available via `pg_config --sharedir`.

See https://www.postgresql.org/docs/current/textsearch-dictionaries.html

Once the custom stop words file has been created, we can run the following SQL:

```sql
CREATE TEXT SEARCH DICTIONARY english_custom (
    TEMPLATE = snowball,
    Language = english,
    StopWords = english_custom
);

CREATE TEXT SEARCH CONFIGURATION public.english_custom (
   COPY = pg_catalog.english
);

ALTER TEXT SEARCH CONFIGURATION public.english_custom
   ALTER MAPPING
      FOR asciiword, asciihword, hword_asciipart, hword, hword_part, word
      WITH english_custom;
```

This should then mean the `english_custom` search dictionary is available.
