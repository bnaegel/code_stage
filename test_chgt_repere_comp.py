#!/usr/bin/python
# -*- coding: Utf-8 -*

#----------------------------------------------------------
# Importation des librairies

from pymorph import *
from matplotlib import pylab as plt
import cv2
import sys
import warnings

from portees_chgt_repere import *
from fonctions_annexes import *
from barres_verticales import *
from notes_compacite import *

#----------------------------------------------------------
# Importation de l'image

img0 = cv2.imread('images/partition2.jpg',0)

# si problème avec la fonction qui grise :  as_grey=True (ne garantit pas des entiers)

#empêche les warning (apparus par magie) quand on ferme la fenêtre de pyplot
warnings.simplefilter("ignore")


#----------------------------------------------------------
# Programme

img1 = cv2.adaptiveThreshold(img0,1,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,21,2)

plt.imshow(img1)
plt.gray()
plt.show()

#on supprime les composantes connexes de trop petite taille
img1 = areaclose(img1,2000)

plt.imshow(img1)
plt.show()

#on supprime tout ce qui n'est pas barre horizontal (à quelques degrés près)
a = 7
img2 = close(img1,seline(a,90))
img3 = close(img1,seline(a,89))
img4 = close(img1,seline(a,88))
img5 = close(img1,seline(a,87))
img6 = close(img1,seline(a,91))
img7 = close(img1,seline(a,92))
img8 = close(img1,seline(a,93))
img9 = close(img1,seline(a,94))

img = union(img2,img3,img4,img5,img6,img7,img8,img9)
plt.imshow(img)
plt.show()

#Vachement long si on trace les points rouges
l1 = trouve_noir_matrice(img)
l2 = les_milieux_liste_de_liste(l1)
l4 = groupe_cinq_points_liste_de_liste(l2)
l4b = ajoute_abscisse(l4)
l4t = liste_sans_liste_vide(l4b)
l5 = split_listes(l4t)

#On a les coordonnées des droites (5) de chaque portée (n)
lprem = premiere_coordonnee_liste_de_liste(l5)
lprem = separe_les_portees(lprem,[])
lsec = deuxieme_coordonnee_liste_de_liste(l5)
lsec = separe_les_portees(lsec,[])
lter = troisieme_coordonnee_liste_de_liste(l5)
lter = separe_les_portees(lter,[])
lqua = quatrieme_coordonnee_liste_de_liste(l5)
lqua = separe_les_portees(lqua,[])
lcin = cinquieme_coordonnee_liste_de_liste(l5)
lcin = separe_les_portees(lcin,[])


#on applique la méthode des moindres carrées pour trouver la droite de la portée

#On calcule les coefficients (A, B, C, D, E, F)
abcdef_prem = calcul_abcdef_plusieurs_listes(lprem)
abcdef_sec = calcul_abcdef_plusieurs_listes(lsec)
abcdef_ter = calcul_abcdef_plusieurs_listes(lter)
abcdef_qua = calcul_abcdef_plusieurs_listes(lqua)
abcdef_cin = calcul_abcdef_plusieurs_listes(lcin)

#On calcule les solutions (b,c) : (pente,ordonnée à l'origine)
solprem = solution_liste(abcdef_prem)
solsec = solution_liste(abcdef_sec)
solter = solution_liste(abcdef_ter)
solqua = solution_liste(abcdef_qua)
solcin = solution_liste(abcdef_cin)

#liste des listes de couples solutions
tab = [solprem,solsec,solter,solqua,solcin]

#A partir des équations, on trace les droites de chaque portée
tracer_droite_liste(solprem,img1)
tracer_droite_liste(solsec,img1)
tracer_droite_liste(solter,img1)
tracer_droite_liste(solqua,img1)
tracer_droite_liste(solcin,img1)

#On affiche l'image et les droites
plt.imshow(img1)
plt.gray()
plt.show()

moy = moyenne_pentes(tab)
try:
	e0 = ecart_moyen(tab)
except IndexError:
	print "erreur lors de la détection des portées"
	sys.exit(1)

#PERTINENT ?
#changement de repère
img2 = changement_repere(img1,moy)

#nouveau tracé des droites
tab2 = changement_de_repere_tableau(img1,tab,moy)
tracer_droite_hori_liste(tab2,img2)

plt.imshow(img2)
plt.show()

#détection des barres verticales
#on ne garde que les barres > 3*écart entre les lignes de portée
img3 = close(img2,seline(3*e0))
plt.imshow(img3)
plt.show()

v1 = trouve_barres_verticales(img3)
#v2 = garde_longues_barres_liste_de_liste(v1,3*e0)
v3 = groupe_deux_points_liste_de_liste(v1)
v4 = ajoute_abscisse(v3)
v4b = liste_sans_liste_vide(v4)
v5 = split_listes(v4b)
v6 = supprime_barres_trop_proches(v5)

trace_verticales_liste(v6)
tracer_droite_hori_liste(tab2,img2)
plt.imshow(img2)
plt.show()

#événement magique qui garde les noires et les croches
cimg = cv2.medianBlur(img0,5)

#on passe en binaire (fait n'importe quoi avec le threshold Gaussien)
cimg = binary(cimg,100)
#cimg = imgbooltoint(cimg) (effet nul, pourquoi ?)

#trace_verticales_liste(v6)
plt.imshow(cimg)
plt.show()


#on enleve les barres ~horizontales possiblement restantes
b = 2*e0 #taille suivant les images !
img52 = close(cimg,seline(b,90))
img53 = close(cimg,seline(b,89))
img54 = close(cimg,seline(b,88))
img55 = close(cimg,seline(b,91))
img56 = close(cimg,seline(b,92))
img57 = close(cimg,seline(b,93))
img58 = close(cimg,seline(b,87))
img59 = close(cimg,seline(b,86))
img60 = close(cimg,seline(b,94))
img61 = close(cimg,seline(b,0))
img62 = union(img52,img53,img54,img55,img56,img57,img58,img59,img60)

img5 = soustraction_img(cimg,img62)
img5 = soustraction_img(img5,img61)

img5 = erode(img5,sedisk(1))
plt.imshow(img5)
plt.show()

#Fond : 0, motifs : 1
img5a = inverse_0_1(img5)
#labellisation
img6 = label(img5a)

plt.imshow(img6)
plt.show()

tab = calcule_aires(img6)
tab = calcule_perimetres(img6,tab)

comp = calcule_compacite(tab)
(n1,img7) = colorie_bons(img6,comp)

plt.imshow(img7)
plt.show()


#on vérifie que les barres verticales sont collées à une note
v8 = bv_collee_notes(v6,n1,e0)
#Listes de la forme [ord1,ord2,ab,ord_note ou 0]
#0 -> barre de mesure ou blanches ou bruit
v9 = liste_listes_note(v8)

#on passe aux croches

#on retire les notes (les croches sont rectangulaires ou ellipsoïdales)
img8 = enleve_notes(cimg,n1)
img8 = erode(img8,sedisk(1))

n2 = recupere_points(img8)
(v10,img9) = bv_collee_croche(v9,n2,e0,img8,1)

n4 = recupere_points(img9)
(n5,img10) = bv_collee_croche2(v10,n4,e0,img9,2)
print n5

img71 = inverse_0_1(img7)

trace_verticales_liste(v6)
tracer_droite_hori_liste(tab2,img2)
plt.imshow(img71)
plt.show()
