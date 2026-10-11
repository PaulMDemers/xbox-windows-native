/* Internal diagnostic state, not a QOM command or guest-facing GPU API. */
typedef struct X259RendererState {
    unsigned next_stage,generation;
    bool failed;
    uint64_t physical,owner;
    uintptr_t surface,callback;
    GLuint texture;
} X259RendererState;
unsigned pgraph_gl_pattern259_stage(NV2AState *,X259RendererState *,
    const X259Admission *,const X259Ref *,const int64_t *,unsigned);
