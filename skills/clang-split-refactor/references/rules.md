# Why the rules exist

Each rule below cost a failed round when the tool lacked it.

**Parse a second configuration.** libclang sees only the active side of each
`#if`. A helper used only under `BUILD_TESTING` looked unused, stayed private to
the wrong file and broke the test build. Merging references from a second
configuration catches most of these; the rest show up when you build both.

**Guard includes only by command-line or platform macros.** A generated
`#if FEATURE` around an include is correct only when `FEATURE` has the same value
in every file. A macro defined in a project header may not be defined yet at the
top of the new file, so the guard silently turns off. `-D` and platform macros do
not have that problem. The source's own guard on the same include is inherited:
an include the source guarded `#if defined(_WIN32)` stays guarded.

**Include headers defining tested macros.** `#if DEMO_VERBOSE` with no
definition in scope is `#if 0`, so moved code quietly changes behavior with no
compile error. Any header in the project that defines a macro the source tests is
added where that macro is used.

**Count complete types from member access and implicit casts.** `p->x` needs the
class of `*p` complete, though the code names only `p`. A derived-to-base
conversion needs the derived class complete. Following only named references
produced "incomplete type" errors in the new files.

**Match helpers by text, move overloads together.** Calls inside templates and
generic lambdas depend on types and are unresolved until instantiation, so the
AST has no reference. Matching anonymous-namespace helper names in the text
recovers them. Text cannot tell overloads apart, so they share a home.

**Deduced return and constexpr stay in headers.** A caller of `auto f()` needs the
body to know the type; a `constexpr` function must be visible for constant
evaluation. They are kept whole in the header and `inline` is added to deduced
functions so the header defines them once.

**Make mutable header variables inline.** A non-const variable moved from an
anonymous namespace into a shared header is defined in every file that includes
it, a duplicate symbol at link time. `inline` keeps one object, and constant
initialization means no change in initialization order.

**Keep pinned spans in place.** Code covered by a digest, a security review or a
contract test must not move, even byte-identically, without that process. Leave
such spans out of every group.

**Build both configurations and stop on failure.** Running tests after a failed
build runs the previous binaries and reports a pass. A gate piped into `tail`
returns `tail`'s status, so a failed build looked green.

**Regenerate instead of hand-merging.** When the base branch moves, merging
generated files by hand mixes old and new extents. Reset the source to the new
base, adjust the plan to the entities that now exist and regenerate.

**Teach source-scanning tests the split.** Contract tests that count call sites
or list members in one file miss the moved code. Concatenate the source and its
split `.cpp` files for call counts (headers would add declaration hits) and
include headers, minus `#include` lines, for member inventories. Tests that copy
the tree to a temp directory must copy the split files as well.

**Header-less groups carry their own declaration includes.** A group with
`header: false` has no header to include the class's declaring header, so each
of its source files takes the full include set. Earlier it worked only when the
header happened to arrive transitively.

**Extend spans to balanced directives.** For an initializer spelled as an
`#if`/`#else` pair, libclang's extent ends inside the active branch. Every moved
span is extended through the matching `#endif`, or the header gets an
unterminated conditional and the source keeps a stray `#else`.

**Keep the source's include vocabulary.** A generated file reaches a project
header through the smallest of the source's own direct includes that brings it
in, spelled as the source spells it. Including the declaring file directly can
break boundary rules that allow only a façade header across a layer.

**Nested types defined out of class go to the support header.** A
`struct Outer::Inner { ... };` in the source is needed complete by every member
file. Treated like a namespace-scope static, it landed in one file and the rest
failed with incomplete types.

**Defaulted and deleted definitions keep their `= default`.** libclang ends the
extent of `X::~X() = default;` at the `)`. Spans are extended past
`= default`/`= delete`, or the moved copy becomes a bare declaration and the
source keeps a stray `= default;`.
