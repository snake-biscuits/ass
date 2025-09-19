# TODOs

copied from `utils_split.md` planning doc


## `editor` tests
 - [ ] `base`
   - [ ] `Brush`
   - [ ] `BrushSide`
   - [ ] `Entity`
   - [ ] `MapFile`
 - [ ] `common`
   - [ ] `comment`
   - [x] `double`
   - [ ] `filepath`
   - [ ] `integer`
   - [ ] `key_value_pair`
   - [ ] `point`
   - [ ] `plane`
   - [ ] `Plane`
   - [ ] `TokenClass`
 - [ ] `id_software`
   - [ ] `BrushSide`
   - [ ] `QuakeMap`
 - [ ] `infinity_ward`
   - [ ] `BrushSide`
   - [ ] `CoD4Map`
   - [ ] `Projection`
 - [ ] `valve`
   - [ ] `map220`
     - [ ] `BrushSide`
     - [ ] `ProjectionAxis`
     - [ ] `Valve220Map`
 - [ ] `valve`
   - [ ] `vmf`
     - [ ] `Brush`
     - [ ] `BrushSide`
     - [ ] `Entity`
     - [ ] `Node`
     - [ ] `ProjectionAxis`
     - [ ] `Vmf`


## Consume `abe`
The first `s` in `ass` stands for Solids
`ass` is handling Brushes, Entities & MapFiles now
So what do we need `abe` for?


## Planned Features
 * `ass[bpy]` Blender-specific tools
   - **for `io_import_rbsp` & `bbbb`**
   - `Material` -> Nodes
   - `Model` -> Object + Bmesh
 * `ass[usd]`
   - wrap `PixarAnimationStudios/OpenUSD`
   - has some neat dependencies
     * OpenSubdiv
     * OpenEXR
     * OpenShadingLanguage
     * PyOpenGL (usdview) GlTF VertexBuffer?
     * PySide6 (usdview) `ass[viewer]`?
 * `Material`
   - Shader abstraction & parsing
   - `bite.Material` compatibility
   - Shader Languages
     * GLSL
     * HLSL
     * OSL
   - Combining shaders w/ variants (`.vcs` w/ `bish`)
