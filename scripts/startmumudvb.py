#! /usr/bin/env python
# -*- coding: iso8859-15 -*-

""" Script de lancement de mumudvb

Auteur : Fr�d�ric Pauget
Licence : GPLv2
"""
import sys, getopt, os
from dvb_base import NotRunning, CarteOqp

if os.getuid() != 101 :
    print "Ce programme doit �tre lanc� par l'utilisateur tv (uid=101)"
    print "Astuce : sudo -u tv %s" % sys.argv[0]
    sys.exit(1)

def usage(erreur=None) :
    if erreur :
	print erreur
    print """Usage : 
  %(p)s start [<numero carte> [<transpondeur>]]: 
      d�marrage le transpondeur donn� sur la carte donn�e, 
      si le transpondeur est omis d�marre celui d�fini dans la conf
      si seul d�marre des flux d�finis dans la conf
  %(p)s stop [numero carte] : 
      arr�te tous les flux des cartes sp�cifi�es, 
      si aucune carte est fournie arr�te tous les flux
      
Les options possibles sont :
    -d ou --debug : affiche tous les messages 
                    et ne daemonize pas crans_dvbsream
    -v ou --verbose : affiche les messages de debuggage
    -q ou --quiet : affiche rien
    --timeout_accord=<nb> : nb de secondesdonn�es pour l'accord""" \
    % { 'p' : sys.argv[0].split('/')[-1] + ' [options]'}
    if not erreur : sys.exit(0)
    else : sys.exit(-1)

# Arguments
try :
    options, args = getopt.getopt(sys.argv[1:], 'hdvq', [ 'help', 'debug' , 'quiet' , 'verbose', 'timeout_accord='] )
except getopt.error, msg :
    sys.stderr.write('%s\n' % msg)
    sys.exit(255)

verbose = 1
timeout_accord = 20
for opt, val in options :
    if opt in [ '-v' , '--verbose' ] :
        verbose = 2
    elif opt in [ '-d' , '--debug' ] :
        verbose = 3
    elif opt == [ '-q' , '--quiet' ] :
        verbose = 0
    elif opt == '--timeout_accord' :
        try:
            timeout_accord = int(val)
        except:
            usage("Valeur de timeout_accord (%s) incorrecte" % val)
    elif opt in [ '-h', '--help' ] :
        usage()

if not args :
    usage('Argument requis')

elif args[0] not in [ 'start', 'stop' ] :
    usage("Commande %s incorrecte" % args[0])


# Carte fournie ?
try :
    cartes = [ int(args[1]) ]
except ValueError :
    usage("Argument %s incorrect (doit �tre le num�ro de carte)." % args[1])
except :
    # Toutes les cartes
    cartes = range(5)
    if verbose > 2 :
        print "Mode debug non permis avec le lancement automatique"
        verbose = 2

if args[0] == 'start' :
    if cartes == range(5) :
        from dvb_conf import conf
        cartes = conf
    else :
        transpondeur = args[2].capitalize()
        from dvb_base import *
        try :
            carte = eval(transpondeur)
            cartes = [ carte(cartes[0]) ] 
        except NameError:
            usage('Transpondeur %s inconnu.' % transpondeur)
    
    
elif args[0] == 'stop' :
    from dvb_base import carte
    cartes = map(carte,cartes)
    
# On effectue l'op�ration demand�e
for carte in cartes :
    carte.verbose = verbose
    carte.timeout_accord = timeout_accord
    try :
        eval('carte.%s()' % args[0])
    except CarteOqp :
        print "Carte %i occup�e, abandon" % carte.card
    except NotRunning :
        # Pas r�ussi � lancer, TODO
        pass
        