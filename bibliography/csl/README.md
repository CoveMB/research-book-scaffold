# CSL styles

Place citation style files here when needed.

The scaffold includes `ieee.csl` from the official CSL/Zotero style repository as the default Quarto and Pandoc Reference List style.

Do not store tracked CSL files in `.pandoc/`; Pandoc Reference List uses that folder as a cache. If a project changes citation style, place the reviewed style file here and update both `manuscript/_quarto.yml` and the Obsidian Pandoc Reference List custom CSL path. Use an absolute path for the Obsidian `cslStylePath` setting.
