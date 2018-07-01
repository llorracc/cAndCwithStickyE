# cAndCwithStickyE-Latest is for sharing among coauthors

The main complication has to do with the bibliography files. If you need to change or add a citation, the way to do it is to put the revised version of a citation in the corresponding [textName]-Add.bib file. On the next compilation by CDC, bibtex will suck in the -Add files into the master economics.bib database, and then the [textName].bib files will get updated (whenever CDC runs his script to do that).

