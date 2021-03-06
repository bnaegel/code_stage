#!/usr/bin/python
# -*- coding: Utf-8 -*

"""Module notes_compacite"""

#----------------------------------------------------------
# Importation des librairies

import numpy as np
from matplotlib import pylab as plt
import matplotlib.pyplot as plt2
from math import *
from pymorph import *

from fonctions_annexes import *
from reconnaissance_clef import *


#----------------------------------------------------------
# Variables globales empiriques

#Distance entre la note et l'extrémité de la barre verticale
dist_note_barre = 5
#Distance entre le symbole croche et l'extrémité de la barre verticale
dist_croche_barre = 5
#Aire minimale acceptée pour être une noire
#aire = 70
#Pourcentage de remplissage du carré pour accepter une double croche
pc_cro = 35

#----------------------------------------------------------
# Fonctions

def calcule_aires(img,ecart):
	a = np.zeros((2,max_matrice(img)+1),np.int)
	pi = 4*atan(1)
	for i in range(img.shape[0]):
		for j in range(img.shape[1]):
			if img[i][j] != 0:
				co = img[i][j]
				a[0][co] = a[0][co] + 1
	for i in range(a.shape[1]):
		#l'aire pour être une note doit au moins être celle d'un cercle de rayon ecart/2
		if a[0][i] < (pi*ecart*ecart)/4:
			a[0][i] = 0
	return a

def calcule_perimetres(img,tab):
	for i in range(1,img.shape[0]-1):
		for j in range(1,img.shape[1]-1):
			if img[i][j] != 0:
				if img[i][j] != img[i-1][j] or img[i][j] != img[i][j-1] or img[i][j] != img[i+1][j] or img[i][j] != img[i][j+1]:
					co = img[i][j]
					tab[1][co] = tab[1][co] + 1
	for i in range(tab.shape[1]):
		tab[0][i] = max(tab[0][i]-tab[1][i],0)
	return tab

def calcule_compacite(tab):
	pi = 4*atan(1)
	a = np.zeros(tab.shape[1],np.float)
	for i in range(len(a)):
		if tab[1][i] != 0:
			a[i] = (4*pi*tab[0][i])/(tab[1][i]*tab[1][i])
	return a

def colorie_bons(img,tab,seuil_comp):
	l = []
	for i in range(img.shape[0]):
		for j in range(img.shape[1]):
			co = img[i][j]
			if tab[co] > seuil_comp:
				img[i][j] = 255
				l.append((i,j))
				#plt.plot(j,i,'ro')
	return (l,img)

#Détermine si la note noire est bien à une position "logique" par rapport à la barre verticale
def existe_noire(i,note,j,ecart,place,coul):
	rep = 0
	e2 = int(round(ecart/2))
	if abs(i - note) <= dist_note_barre:
		rep = i
		if place == 'b':
			c2 = plt2.Circle(((2*j-ecart)/2,i),e2,color=coul)
			plt2.gcf().gca().add_artist(c2)
		else:
			c2 = plt2.Circle(((2*j+ecart)/2,i),e2,color=coul)
			plt2.gcf().gca().add_artist(c2)
	return rep

#On associe les notes et les barres verticales qui s'interceptent
def bv_collee_notes(bv,note,ecart):
	for elt in bv:
		for elt2 in note:
			if (elt[2] == elt2[1]) and (elt2[0] < elt[1]) and (elt2[0] > elt[0]):
				if len(elt) < 4:
					bas = existe_noire(elt[1],elt2[0],elt[2],ecart,'b','red')
					haut = existe_noire(elt[0],elt2[0],elt[2],ecart,'h','red')
					if bas !=0:
						#on réhausse un peu la note
						elt.append(bas-2)
					elif haut != 0:
						elt.append(haut-1)
	return bv
	
def liste_notes(liste):
	somme = 0
	l = []
	if len(liste) > 4:
		for i in range(3,len(liste)):
			somme = somme + liste[i]
			l.extend(liste[:3])
			l.append(somme/(len(liste)-3))
	elif len(liste) == 3:
		l = liste
		l.append(0)
	else:
		l = liste
	return l

def liste_listes_note(liste):
	l = []
	for elt in liste:
		l.append(liste_notes(elt))
	return l

#--------------------------------------------------------------
#Croches
	
def enleve_notes(img,liste):
	for elt in liste:
		(i,j) = elt
		#on retire les noires précédemment sélectionnées en les mettant en "blanc - fond"
		img[i][j] = 1
	return img
			
def recupere_points(img):
	l = []
	for i in range(img.shape[0]):
		for j in range(img.shape[1]):
			#on récupère les pixels noirs
			if img[i][j] != 1 or img[i][j] == False:
				#plt.plot(j,i,'ro')
				l.append((i,j))
	return l

#Détermine si la croche est bien à une position "logique" par rapport à la barre verticale
def existe_croche(i,croche,j,ecart,place,numero_croche):
	rep = 0
	e2 = int(round(ecart/2))
	if abs(i - croche) <= (numero_croche-1)*e2+dist_croche_barre:
		rep = 1
		if place == 'b':
			p = plt2.Rectangle((j-e2,i-e2-(numero_croche-1)*ecart),e2,e2,color='b')
			plt2.gcf().gca().add_artist(p)
		else:
			p = plt2.Rectangle((j,i+ecart*(numero_croche-1)),e2,e2,color='b')
			plt2.gcf().gca().add_artist(p)
	return rep

#identifie une éventuelle croche en haut d'une barre verticale
def existe_croche_haut(img,ecart,i,j,pc_cro):
	somme = 0
	rep = 0
	ecart = int(round(ecart))
	e2 = int(round(ecart/2))
	for x in range(i,i+e2):
		for y in range(j-e2,j):
			if x < img.shape[0] and y < img.shape[1]:
				if img[x][y] == 0:
					somme = 1 + somme
	if somme*100 >= pc_cro*e2*e2:
		p = plt2.Rectangle((j,i),e2,e2,color='b')
		plt2.gcf().gca().add_artist(p)
		rep = 1
	else:
		somme = 0
		for x in range(i,i+e2):
			for y in range(j,j+e2):
				if x < img.shape[0] and y < img.shape[1]:
					if img[x][y] == 0:
						somme = 1 + somme
		if somme*100 >= pc_cro*e2*e2:
			p = plt2.Rectangle((j,i),e2,e2,color='b')
			plt2.gcf().gca().add_artist(p)
			rep = 1
	return rep

#identifie une éventuelle croche en bas d'une barre verticale
def existe_croche_bas(img,ecart,i,j,pc_cro):
	somme = 0
	rep = 0
	ecart = int(round(ecart))
	e2 = int(round(ecart/2))
	for x in range(i-e2,i):
		for y in range(j-e2,j):
			if x < img.shape[0] and y < img.shape[1]:
				if img[x][y] == 0:
					somme = 1 + somme
	if somme*100 >= pc_cro*e2*e2:
		p = plt2.Rectangle((j-e2,i-e2),e2,e2,color='b')
		plt2.gcf().gca().add_artist(p)
		rep = 1
	else:
		somme = 0
		for x in range(i-e2,i):
			for y in range(j,j+e2):
				if x < img.shape[0] and y < img.shape[1]:
					if img[x][y] == 0:
						somme = 1 + somme
		if somme*100 >= pc_cro*e2*e2:
			p = plt2.Rectangle((j-e2,i-e2),e2,e2,color='b')
			plt2.gcf().gca().add_artist(p)
			rep = 1
	return rep

#on utilise la méthode par amas faute de mieux
def existe_autre_croche(img,bv,ecart,nbr_croches):
	ecart = int(round(ecart))
	for elt in bv:
		if len(elt) == 5:
			if elt[4] < 2:
				if elt[4] == 0: #on cherche en bas
					for i in range(1,nbr_croches):
						elt[4] = 1 + existe_croche_bas(img,ecart,elt[1]-i*ecart,elt[2],pc_cro) + elt[4]
				elif elt[4] == 1: #on cherche en haut
					for i in range(1,nbr_croches):
						elt[4] = existe_croche_haut(img,ecart,elt[0]+i*ecart,elt[2],pc_cro) + elt[4]
	return bv


def bv_collee_croche(bv,croche,ecart,img,numer):
	e2 = int(round(ecart/2))
	for elt in bv:
		for elt2 in croche:
			if (elt[2] == elt2[1]) and (elt2[0] < elt[1]) and (elt2[0] > elt[0]):		
				if (elt[3] != 0) and (len(elt) < 5):
					bas = existe_croche(elt[1],elt2[0],elt[2],ecart,'b',numer)
					haut = existe_croche(elt[0],elt2[0],elt[2],ecart,'h',numer)
					if bas !=0:
						elt.append(0) 
					elif haut != 0:
						elt.append(1) 
	#on renvoie la liste des barres verticales augmentées
	return bv

#Pour les barres verticales qui n'ont pas de croches, on met leur nombre à 0
def liste_croches(liste):
	l = []
	if len(liste) == 4:
		l = liste
		l.append(0)
	else:
		l = liste
	return l

def liste_listes_croche(liste):
	l = []
	for elt in liste:
		l.append(liste_croches(elt))
	return l

#--------------------------------------------------------------
#Noms des notes

def notes_par_portees(liste,tab,ecart):
	#on crée un tableau de la taille "nombre de portées"
	l = []
	for i in range(len(tab[0])):
		l.append([])
		
	#on parcourt les portées
	for i in range(len(tab[0])):
		for j in range(len(liste)):
			m = (liste[j][1]+liste[j][0])/2 
			#si le milieu de la barre appartient à la portée i, on l'ajoute à la case i
			if m >= tab[0][i]-2*ecart and m <= tab[4][i]+2*ecart:
				l[i].append(liste[j])
	return l

#Notes pour la clef de sol
#j est l'ordonnée de l'extrémité de la barre où se trouve la note
#x est le numéro de la portée (commence à 0)
def determine_note_sol(j,tab,ecart,inter_note,x):
	rep = ''
	#notes sur les lignes
	if j > tab[0][x]-inter_note and j < tab[0][x]+inter_note:
		rep = 'fa'
	elif j > tab[1][x]-inter_note and j < tab[1][x]+inter_note:
		rep = 're'
	elif j > tab[2][x]-inter_note and j < tab[2][x]+inter_note:
		rep = 'si'
	elif j > tab[3][x]-inter_note and j < tab[3][x]+inter_note:
		rep = 'sol'
	elif j > tab[4][x]-inter_note and j < tab[4][x]+inter_note:
		rep = 'mi grave'
	#notes entre les lignes
	elif j > (tab[0][x]+tab[1][x])/2-inter_note and j < (tab[0][x]+tab[1][x])/2+inter_note:
		rep = 'mi'
	elif j > (tab[1][x]+tab[2][x])/2-inter_note and j < (tab[2][x]+tab[1][x])/2+inter_note:
		rep = 'do'
	elif j > (tab[2][x]+tab[3][x])/2-inter_note and j < (tab[3][x]+tab[2][x])/2+inter_note:
		rep = 'la'
	elif j > (tab[3][x]+tab[4][x])/2-inter_note and j < (tab[4][x]+tab[3][x])/2+inter_note:
		rep = 'fa grave'
	#notes en-dessous des lignes
	elif j > (2*tab[4][x]+ecart)/2-inter_note and j < (2*tab[4][x]+ecart)/2+inter_note:
		rep = 're grave'
	elif j > tab[4][x]+ecart-inter_note and j < tab[4][x]+ecart+inter_note:
		rep = 'do grave'
	elif j > (2*tab[4][x]+3*ecart)/2-inter_note and j < (2*tab[4][x]+3*ecart)/2+inter_note:
		rep = 'si grave'
	elif j > tab[4][x]+2*ecart-inter_note and j < tab[4][x]+2*ecart+inter_note:
		rep = 'la grave'
	#notes au-dessus des lignes
	elif j > (2*tab[0][x]-ecart)/2-inter_note and j < (2*tab[0][x]-ecart)/2+inter_note:
		rep = 'sol aigu'
	elif j > tab[0][x]-ecart-inter_note and j < tab[0][x]-ecart+inter_note:
		rep = 'la aigu'
	elif j > (2*tab[0][x]-3*ecart)/2-inter_note and j < (2*tab[0][x]-3*ecart)/2+inter_note:
		rep = 'si aigu'
	elif j > tab[0][x]-2*ecart-inter_note and j < tab[0][x]-2*ecart+inter_note:
		rep = 'do aigu'
	return rep

#Notes pour le clef de fa
def determine_note_fa(j,tab,ecart,inter_note,x):
	rep = ''
	#notes sur les lignes
	if j > tab[0][x]-inter_note and j < tab[0][x]+inter_note:
		rep = 'la aigu'
	elif j > tab[1][x]-inter_note and j < tab[1][x]+inter_note:
		rep = 'fa'
	elif j > tab[2][x]-inter_note and j < tab[2][x]+inter_note:
		rep = 're'
	elif j > tab[3][x]-inter_note and j < tab[3][x]+inter_note:
		rep = 'si'
	elif j > tab[4][x]-inter_note and j < tab[4][x]+inter_note:
		rep = 'sol'
	#notes entre les lignes
	elif j > (tab[0][x]+tab[1][x])/2-inter_note and j < (tab[0][x]+tab[1][x])/2+inter_note:
		rep = 'sol aigu'
	elif j > (tab[1][x]+tab[2][x])/2-inter_note and j < (tab[2][x]+tab[1][x])/2+inter_note:
		rep = 'mi'
	elif j > (tab[2][x]+tab[3][x])/2-inter_note and j < (tab[3][x]+tab[2][x])/2+inter_note:
		rep = 'do'
	elif j > (tab[3][x]+tab[4][x])/2-inter_note and j < (tab[4][x]+tab[3][x])/2+inter_note:
		rep = 'la'
	#notes en-dessous des lignes
	elif j > (2*tab[4][x]+ecart)/2-inter_note and j < (2*tab[4][x]+ecart)/2+inter_note:
		rep = 'fa grave'
	elif j > tab[4][x]+ecart-inter_note and j < tab[4][x]+ecart+inter_note:
		rep = 'mi grave'
	elif j > (2*tab[4][x]+3*ecart)/2-inter_note and j < (2*tab[4][x]+3*ecart)/2+inter_note:
		rep = 're grave'
	elif j > tab[4][x]+2*ecart-inter_note and j < tab[4][x]+2*ecart+inter_note:
		rep = 'do grave'
	#notes au-dessus des lignes
	elif j > (2*tab[0][x]-ecart)/2-inter_note and j < (2*tab[0][x]-ecart)/2+inter_note:
		rep = 'si aigu'
	elif j > tab[0][x]-ecart-inter_note and j < tab[0][x]-ecart+inter_note:
		rep = 'do aigu'
	elif j > (2*tab[0][x]-3*ecart)/2-inter_note and j < (2*tab[0][x]-3*ecart)/2+inter_note:
		rep = 're aigu'
	elif j > tab[0][x]-2*ecart-inter_note and j < tab[0][x]-2*ecart+inter_note:
		rep = 'mi aigu'
	return rep

#Notes pour le clef d'ut
def determine_note_ut(j,tab,ecart,inter_note,x):
	rep = ''
	#notes sur les lignes
	if j > tab[0][x]-inter_note and j < tab[0][x]+inter_note:
		rep = 'sol'
	elif j > tab[1][x]-inter_note and j < tab[1][x]+inter_note:
		rep = 'mi'
	elif j > tab[2][x]-inter_note and j < tab[2][x]+inter_note:
		rep = 'do'
	elif j > tab[3][x]-inter_note and j < tab[3][x]+inter_note:
		rep = 'la'
	elif j > tab[4][x]-inter_note and j < tab[4][x]+inter_note:
		rep = 'fa grave'
	#notes entre les lignes
	elif j > (tab[0][x]+tab[1][x])/2-inter_note and j < (tab[0][x]+tab[1][x])/2+inter_note:
		rep = 'fa'
	elif j > (tab[1][x]+tab[2][x])/2-inter_note and j < (tab[2][x]+tab[1][x])/2+inter_note:
		rep = 're'
	elif j > (tab[2][x]+tab[3][x])/2-inter_note and j < (tab[3][x]+tab[2][x])/2+inter_note:
		rep = 'si'
	elif j > (tab[3][x]+tab[4][x])/2-inter_note and j < (tab[4][x]+tab[3][x])/2+inter_note:
		rep = 'sol grave'
	#notes en-dessous des lignes
	elif j > (2*tab[4][x]+ecart)/2-inter_note and j < (2*tab[4][x]+ecart)/2+inter_note:
		rep = 'mi grave'
	elif j > tab[4][x]+ecart-inter_note and j < tab[4][x]+ecart+inter_note:
		rep = 're grave'
	elif j > (2*tab[4][x]+3*ecart)/2-inter_note and j < (2*tab[4][x]+3*ecart)/2+inter_note:
		rep = 'do grave'
	elif j > tab[4][x]+2*ecart-inter_note and j < tab[4][x]+2*ecart+inter_note:
		rep = 'sol grave'
	#notes au-dessus des lignes
	elif j > (2*tab[0][x]-ecart)/2-inter_note and j < (2*tab[0][x]-ecart)/2+inter_note:
		rep = 'la aigu'
	elif j > tab[0][x]-ecart-inter_note and j < tab[0][x]-ecart+inter_note:
		rep = 'si aigu'
	elif j > (2*tab[0][x]-3*ecart)/2-inter_note and j < (2*tab[0][x]-3*ecart)/2+inter_note:
		rep = 'do aigu'
	elif j > tab[0][x]-2*ecart-inter_note and j < tab[0][x]-2*ecart+inter_note:
		rep = 're aigu'
	return rep


#bv : liste des barres verticales
#tab : ordonnées des portées
#ecart : écart moyen entre les portées
def nom_notes(bv,tab,ecart,list_img,sol,fa,ut,dist):
	rep = ''
	rep2 = ''
	
	#détermination de l'intervalle [X-inter_note,X+internote] dans lequel se trouve la note
	if ecart < 10:
		inter_note = 2
	elif ecart < 20:
		inter_note = 3
	else:
		inter_note = 5
		
	for i in range(len(bv)):
	
		#pour une portée, on détermine la clef
		clef,ab = cherche_bonne_clef(list_img[i],sol,fa,ut,tab,dist)
	
		for elt in bv[i]:
			#si on a une note et qu'elle se trouve après la clef
			if (elt[3] != 0 or elt[5] != 0) and elt[2] > ab:
			
				if elt[3] != 0:
					n = elt[3]
				elif elt[5] != 0:
					n = elt[5]
				
				#notes
				if clef == 'sol':
					rep = determine_note_sol(n,tab,ecart,inter_note,i)
				elif clef == 'fa':
					rep = determine_note_fa(n,tab,ecart,inter_note,i)
				elif clef == 'ut':
					rep = determine_note_ut(n,tab,ecart,inter_note,i)
			
				#croches
				if elt[4] == 1:
					rep2 = 'croche '+rep
					elt.append(rep2)
				elif elt[4] == 2:
					rep2 = 'double croche '+rep
					elt.append(rep2)
				elif elt[4] == 3:
					rep2 = 'triple croche '+rep
					elt.append(rep2)
				elif elt[5] != 0:
					rep2 = 'blanche '+rep
					elt.append(rep2)
				else:
					elt.append(rep)
				
				#on affiche le nom de la note sous celle-ci
				plt2.text(elt[2]-1,elt[1]+4*ecart,rep,fontsize=7,color='g')
	return bv

#------------------------------------------------------------
#Blanches

#on retire les portées de l'image
def enleve_portees(img,soluce):
	for x in range(img.shape[0]):
		for y in range(img.shape[1]):
			if round(y*soluce[0]+soluce[1]) == x:
				#img[x][y] = 1
				#img[x-1][y] = 1
				img[x+1][y] = 1 #peu précis mais imprécision des droites détectées oblige	
	return img

def enleve_portees_liste(img,liste):
	img1 = np.zeros(img.shape,np.int)
	img2 = np.zeros(img.shape,np.int)
	for elt in liste:
		for elt2 in elt:
			img1 = enleve_portees(img,elt2)
			img2 = union(img2,img1)
	return img2
	
def cherche_blanche(bv,note,ecart):
	for elt in bv:
		#si on a pas encore de note
		if elt[3] == 0:	
			for elt2 in note:
				if (elt[2] == elt2[1]) and (elt2[0] < elt[1]) and (elt2[0] > elt[0]):
					if len(elt) < 6:
						bas = existe_noire(elt[1],elt2[0],elt[2],ecart,'b','magenta')
						haut = existe_noire(elt[0],elt2[0],elt[2],ecart,'h','magenta')
						if bas !=0:
							#on réhausse un peu la note
							elt.append(bas-2)
						elif haut != 0:
							elt.append(haut-1)
	return bv

def liste_toutes_notes(note):
	for elt in note:
		if len(elt) < 6:
			elt.append(0)
	return note


#----------------------------------------------------------
# Barres de mesure

def barres_mesure(bv,ecart):
	l = []
	for elt in bv:
		if elt[3] == 0 and elt[5] == 0:
			longueur = elt[1]-elt[0]
			#une barre de mesure doit au moins faire la largeur de la portée
			if longueur >= 4*ecart:
				l.append(elt)
				plt.plot([elt[2],elt[2]],[elt[1],elt[0]],'b',linewidth=3)
		else:
			l.append(elt)
	return l











