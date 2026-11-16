# NAO Customization

Petites personnalisations pour mes environnements Linux, Windows et autres.
Chaque personnalisation reste autonome : ses fichiers, ses prérequis et ses
instructions sont regroupés dans son dossier.

## Arborescence

```text
linux/
  plymouth/
    nao-bounce/    # Prototype : NAO rebondit pendant le démarrage
windows/          # Futures personnalisations Windows
shared/           # Ressources communes aux différents systèmes
```

## Premier projet

[NAO Bounce](linux/plymouth/nao-bounce/README.md) est un thème Plymouth de départ.
Il utilise une mascotte robot provisoire, à remplacer par le vrai visuel de NAO.

## Ajouter une personnalisation

Créer un dossier sous le système concerné, par exemple `linux/terminal/mon-theme`
ou `windows/terminal/mon-theme`. Ajouter un README décrivant le résultat attendu,
les prérequis, l'installation, la vérification et la désinstallation. Placer les
ressources propres au projet dans son dossier `assets/` ; réserver `shared/` aux
ressources réellement communes. Ne pas versionner de secrets ou de configurations
personnelles contenant des identifiants.
