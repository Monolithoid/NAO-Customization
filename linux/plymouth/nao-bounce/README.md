# NAO Bounce — prototype Plymouth

Une mascotte robot rebondit au centre d'un fond bleu sombre pendant le démarrage.
Le PNG fourni est un dessin provisoire créé pour ce dépôt, pas un visuel officiel
de NAO. Remplacer `assets/nao.png` par un PNG transparent de dimensions similaires
(192 × 192) pour personnaliser le personnage. Le mouvement se règle dans
`nao-bounce.script` : amplitude `45`, vitesse `3`.

## Prérequis

Une machine Linux utilisant Plymouth avec son module `script`. Le paquet et les
outils de sélection du thème dépendent de la distribution. Aucun secret ni service
externe n'est nécessaire. Ce thème ne concerne pas Windows.

## Installation manuelle

Depuis ce dossier, sur une machine de test avec Plymouth installé :

```sh
sudo install -d /usr/share/plymouth/themes/nao-bounce
sudo install -m 644 nao-bounce.plymouth nao-bounce.script assets/nao.png /usr/share/plymouth/themes/nao-bounce/
```

La sélection du thème et la reconstruction de l'initramfs sont spécifiques à la
distribution. Noter le thème actuel avant toute modification.

Sur les distributions proposant `plymouth-set-default-theme` :

```sh
plymouth-set-default-theme                 # noter la valeur pour la restauration
sudo plymouth-set-default-theme -R nao-bounce
```

Sur Debian/Ubuntu utilisant les alternatives :

```sh
update-alternatives --display default.plymouth   # noter la cible actuelle
sudo update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/nao-bounce/nao-bounce.plymouth 100
sudo update-alternatives --config default.plymouth
sudo update-initramfs -u
```

## Vérification

Vérifier le rendu sur une VM avec console graphique avant d'utiliser ce prototype
sur sa machine principale. Contrôler l'animation, les messages et, si applicable,
la saisie du mot de passe de déchiffrement. Plymouth dépend de la console et du
matériel graphique : servir les fichiers dans un navigateur ne teste pas le thème.
Le rendu et ces interactions n'ont pas encore été validés dans Plymouth.

## Désinstallation

Rétablir le thème précédent et reconstruire l'initramfs avec la méthode de votre
distribution. Avec les alternatives, sélectionner d'abord l'ancienne cible puis
retirer l'inscription :

```sh
sudo update-alternatives --remove default.plymouth /usr/share/plymouth/themes/nao-bounce/nao-bounce.plymouth
sudo update-initramfs -u
```

Après restauration, supprimer uniquement le dossier installé `nao-bounce`.
