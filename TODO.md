# TODOs

copied from `utils_split.md` planning doc


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
 * `bite.Material` support
   - `bite` should extend `ass` w/ parsed file formats
 * `khronos.Dae` (`model/vnd.collada+xml`)
   - Originally created at Sony Computer Entertainment
   - COLLADA DOM uses SCEA Shared Source License 1.0
   - Wikipedia page is a good reference
 * `blockbench.BBModel`
   - `text/json` format used with Minecraft (Figura)
 * pip extras
   - `viewer` (same dependencies as `usdview`)
