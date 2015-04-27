subject to een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_zn_eigen_team
    {p in Zangleiding_persons inter Muziek_teams, w in weeks}:
    Muziek[p,w] >= Zangleiding[p,w];
    
#subject to een_koster_draait_dubbele_diensten
#    {k in Koster_persons, z in 0..(aantal_weken/2-1)}:
#    kosterdienst[k,eerste_week+2*z] = kosterdienst[k,eerste_week+2*z+1];

#subject to een_koster_heeft_gewenste_ritme
#    {k in Koster_persons, z1 in zondagen_uitgebreid}:
#    (sum {z2 in z1..(z1 + kosterritme[k]-1): z2 in zondagen} kosterdienst[k,z2])
#        <= 2 + kosteruitritme[k,z1];

#subject to twee_Hulpkoster_persons
#    {z in zondagen}:
#    (sum {h in Hulpkoster_persons} hulpkosterdienst[h,z]) = 2;

