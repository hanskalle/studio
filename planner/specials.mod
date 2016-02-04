var wijngaardenbreuk {weeks}, binary;
var matthijszonderlianne, binary;
var liannezondermatthijs, binary;
set gebedsmannen := {'Hans_Z', 'Hans_K', 'Wim_R', 'Andreas', 'Roeland', 'Jan'};

+ (sum {w in weeks} 8 * wijngaardenbreuk[w])
+ 10 * matthijszonderlianne
+ 20 * liannezondermatthijs

#ignore minimum_Beamer
#ignore maximum_Beamer
#ignore rest_Beamer
#ignore rest_history_Beamer
#ignore minimum_Leiding_Blauw
#ignore maximum_Leiding_Blauw
#ignore rest_Leiding_Blauw
ignore rest_history_Leiding_Blauw
#ignore rest_history_Beamer
#ignore minimum_Geluid
#ignore maximum_Geluid
#ignore rest_Geluid
#ignore rest_history_Geluid
#ignore minimum_Hoofdkoster
#ignore maximum_Hoofdkoster
#ignore rest_Hoofdkoster
#ignore rest_history_Hoofdkoster
#ignore minimum_Hulpkoster
#ignore maximum_Hulpkoster
#ignore rest_Hulpkoster
#ignore rest_history_Hulpkoster
#ignore minimum_Koffie
#ignore maximum_Koffie
#ignore rest_Koffie
#ignore rest_history_Koffie
#ignore minimum_Muziek
#ignore maximum_Muziek
#ignore rest_Muziek
#ignore rest_history_Muziek
#ignore minimum_Leiding_Rood
#ignore maximum_Leiding_Rood
#ignore rest_Leiding_Rood
#ignore rest_Groep_Rood
ignore rest_history_Leiding_Rood
#ignore minimum_Welkom
#ignore maximum_Welkom
#ignore rest_Welkom
#ignore rest_history_Welkom
#ignore minimum_Leiding_Wit
#ignore maximum_Leiding_Wit
#ignore rest_Leiding_Wit
#ignore rest_history_Leiding_Wit
#ignore rest_Groep_Wit
#ignore minimum_Zangleiding
#ignore maximum_Zangleiding
#ignore rest_Zangleiding
#ignore rest_history_Zangleiding

subject to jeugddienst1:
    Zangleiding['Jolanda',5] = 1;

subject to eerstedienst:
    Zangleiding['Wim_R',0] = 1;

subject to paasdienst:
    Zangleiding['Jolanda',12] = 1;

subject to jeugddienst2:
    Leiding_Rood['In_de_dienst',5] = 1;

subject to Bas_alleen_beamer_als_in_de_dienst {w in weeks}:
    Beamer['Bas',w] <= Leiding_Rood['In_de_dienst',w];

subject to Een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_eigen_team1
    {p in Zangleiding_persons inter Muziek_teams, w in weeks}:
    Muziek[p,w] >= Zangleiding[p,w];

subject to Een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_eigen_team2
    {p in Zangleiding_persons inter Muziek_persons, t in Muziek_teams, w in weeks: Muziek_member[t, p]}:
    Muziek[t,w] >= Zangleiding[p,w];

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

subject to Rachel_geen_gebed_met_man {w in weeks}:
    Gebed['Rachel',w] <= 1 - (sum {p in gebedsmannen} Gebed[p,w]);

subject to Rachel_niet_als_Tim_een_taak_heeft {w in weeks}:
    Gebed['Rachel',w] <= 1 - Muziek['Tim',w] - Leiding_Rood['Tim',w];

subject to Geen_mannen_samen_gebed {w in weeks}:
    (sum {p in gebedsmannen} Gebed[p,w]) <= 1;

subject to Liesbeth_graag_met_haar_man {w in weeks}:
    Gebed['Liesbeth_Z',w] = Gebed['Hans_Z',w];

subject to Nora_graag_met_haar_man {w in weeks}:
    Gebed['Nora',w] = Gebed['Wim_R',w];