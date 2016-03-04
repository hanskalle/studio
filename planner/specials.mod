var wijngaardenbreuk {weeks}, binary;
var matthijszonderlianne, binary;
var liannezondermatthijs, binary;
set gebedsmannen := {'Hans_Z', 'Hans_K', 'Wim_R', 'Andreas', 'Roeland', 'Jan'};


+ (sum {w in weeks} 8 * wijngaardenbreuk[w])
+ 10 * matthijszonderlianne
+ 20 * liannezondermatthijs
+ (sum {w in weeks} 8 * geenrustjolanda[w])


#ignore minimum_.*


subject to Bas_tot_vakantie_alleen_beamer_als_Rood_in_de_dienst {w in weeks: w < 27}:
    Beamer['Bas',w] <= Leiding_Rood['In_de_dienst',w];

subject to Een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_eigen_team
    {p in Zangleiding_persons inter Muziek_leaders, w in weeks}:
    Muziek[p,w] >= Zangleiding[p,w];

subject to Jolanda_geen_zangleiding_tegelijkertijd_met_Wim_A_hulpkoster
    {w in weeks}:
    Zangleiding['Jolanda',w] + Hulpkoster['Wim_A',w] <= 1;

subject to Als_Matthuis_hoofdkoster_is_doet_Lianne_welkom
    {w in weeks}:
    Hoofdkoster['Matthijs',w] <= Welkom['Lianne',w] + matthijszonderlianne;

subject to Als_Lianne_welkom_doet_is_Matthijs_hoofdkoster
    {w in weeks}:
    Welkom['Lianne',w] <= Hoofdkoster['Matthijs',w] + liannezondermatthijs;

subject to Rachel_leidt_groep_Blauw_wanneer_Tim_groep_Rood_leidt
    {w in weeks}:
    Leiding_Rood['Tim',w] <= Leiding_Blauw['Rachel',w] + wijngaardenbreuk[w];

subject to Tim_leidt_groep_Rood_wanneer_Rachel_groep_Blauw_leidt
    {w in weeks}:
    Leiding_Blauw['Rachel',w] <= Leiding_Rood['Tim',w] + wijngaardenbreuk[w];

subject to Roel_hulpkoster_met_hoofdkoster_Herman
    {w in weeks}:
    Hulpkoster['Roel',w] <= Hoofdkoster['Herman',w];

subject to Rachel_geen_gebed_met_man {w in weeks}:
    Gebed['Rachel',w] <= 1 - (sum {p in gebedsmannen} Gebed[p,w]);

subject to Rachel_geen_gebed_als_Tim_een_taak_heeft {w in weeks}:
    Gebed['Rachel',w] <= 1 - Muziek['Tim',w] - Leiding_Rood['Tim',w];

subject to Geen_mannen_samen_gebed {w in weeks}:
    (sum {p in gebedsmannen} Gebed[p,w]) <= 1;

subject to Nora_gebed_met_Wim_R
    {w in weeks}:
    Gebed['Nora',w] <= Gebed['Wim_R',w];

subject to Liesbeth_Z_gebed_met_Hans_Z
    {w in weeks}:
    Gebed['Liesbeth_Z',w] <= Gebed['Hans_Z',w];

subject to Wenny_gebed_met_Jan_P
    {w in weeks}:
    Gebed['Wenny',w] <= Gebed['Jan_P',w];

display Muziek_too_early;