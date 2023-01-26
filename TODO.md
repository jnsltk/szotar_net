# szotar_net 
szotar_net is a command line based client for the Chinese-Hungarian dictionary provided by Szotar.net

### Todo (NOT in order of urgency)

- [ ] Add settings menu
  - [ ] Option for Trad/Simp
  - [ ] Option for zhuyin/pinyin
  - [ ] Option to set custom colours
  - [ ] Toggle for the Taiwanese word feature
- [ ] Feature to say if a word is Mainland only, gives Taiwanese alternative
- [ ] Interactive shell mode
- [ ] Save/serialize session object
- [ ] History/cache (might be illegal, so maybe not)
- [ ] Favourites (??)
- [ ] TTS
- [ ] Localisation
  - [ ] Chinese-language interface (Both Traditional and Simplified)
  - [ ] English interface
- [ ] Word frequency
  - [ ] TOCFL
  - [ ] HSK
- [ ] Export favourites to Anki deck (again, there might be copyright issues)
- [ ] Make an anki extension out of the base code that loads the info to the cards
- [ ] --help 
- [ ] Manpage
- [ ] Is it possible to make it faster?
- [ ] Add loading animation (| / 一 \ |) ...
- [ ] Reduce the amount of Chinese language related packages, there's a lot of overlap in functionality
- [ ] Use exceptions
- [ ] Option to regenerate/reset config
- [ ] Ask for Szotar.net credentials on first run

### In progress

- [ ] Add settings menu
  - [ ] Option for Trad/Simp
  - [ ] Option for zhuyin/pinyin
  - [ ] Option to set custom colours
  - [ ] Toggle for the Taiwanese word feature
- [ ] Show option for alternative pronunciations (eg. 為)

### Done
- [x] Properly scraping all data from a szotar.net entry
- [x] Loading it in an Entry object
- [x] Printing it
- [x] Add colours, refactor printing
  - [x] Pinyin colours
  - [x] Colours for different types of texts (increase readability)
- [x] Save/serialize session object
- [x] Interactive shell mode
- [x] Build a package, make it installable via pip or something
  - [x] Fix paths (IMPORTANT!!)
