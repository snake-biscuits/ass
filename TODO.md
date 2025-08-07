# TODOs

copied from `utils_split.md` planning doc

## Tests
 * migrate from `bsp_tool`
   - will require `pytest`


## `pyproject.toml`
 * dependencies


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
