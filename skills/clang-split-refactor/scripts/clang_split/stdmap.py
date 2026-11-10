"""Canonical standard / Qt header for a referenced declaration.

Including the header a name is documented in, rather than the libc++/libstdc++
internal file that declares it, keeps generated includes portable.
"""
import os
from .cx import ci, is_system, is_stdlib
K = ci.CursorKind
T = {}
def _a(h, names):
    for n in names.split():
        T[n] = h
_a('<mutex>', 'mutex recursive_mutex lock_guard scoped_lock unique_lock call_once once_flag try_lock defer_lock adopt_lock')
_a('<shared_mutex>', 'shared_mutex shared_lock')
_a('<atomic>', 'atomic atomic_bool atomic_int atomic_size_t atomic_uint64_t atomic_flag memory_order memory_order_relaxed memory_order_acquire memory_order_release memory_order_acq_rel memory_order_seq_cst atomic_thread_fence')
_a('<vector>', 'vector erase erase_if')
_a('<string>', 'string basic_string to_string wstring u8string stoi stoul stoull char_traits getline')
_a('<string_view>', 'string_view basic_string_view u8string_view wstring_view')
_a('<optional>', 'optional nullopt nullopt_t make_optional bad_optional_access')
_a('<expected>', 'expected unexpected unexpect bad_expected_access')
_a('<variant>', 'variant get_if holds_alternative visit monostate variant_alternative_t')
_a('<memory>', 'unique_ptr shared_ptr weak_ptr make_unique make_shared enable_shared_from_this addressof default_delete static_pointer_cast dynamic_pointer_cast allocate_shared')
_a('<functional>', 'function invoke ref cref reference_wrapper bind_front hash less greater equal_to identity')
_a('<utility>', 'move forward exchange pair make_pair swap declval as_const in_place in_place_t index_sequence make_index_sequence to_underlying unreachable cmp_less')
_a('<stop_token>', 'stop_token stop_source stop_callback nostopstate')
_a('<thread>', 'thread jthread this_thread')
_a('<chrono>', 'chrono')
_a('<filesystem>', 'filesystem')
_a('<span>', 'span dynamic_extent')
_a('<array>', 'array to_array')
_a('<map>', 'map multimap')
_a('<set>', 'set multiset')
_a('<unordered_map>', 'unordered_map')
_a('<unordered_set>', 'unordered_set')
_a('<deque>', 'deque')
_a('<list>', 'list')
_a('<queue>', 'queue priority_queue')
_a('<cstddef>', 'size_t nullptr_t byte ptrdiff_t max_align_t')
_a('<cstdint>', 'uint8_t uint16_t uint32_t uint64_t int8_t int16_t int32_t int64_t uintptr_t intptr_t uintmax_t intmax_t')
_a('<algorithm>', 'min max minmax clamp find find_if find_if_not sort stable_sort any_of all_of none_of remove remove_if copy copy_if copy_n transform equal fill count count_if reverse unique lower_bound upper_bound binary_search for_each max_element min_element mismatch search replace rotate partition nth_element includes set_difference set_intersection set_union lexicographical_compare ranges views')
_a('<exception>', 'exception exception_ptr current_exception rethrow_exception make_exception_ptr terminate uncaught_exceptions nested_exception')
_a('<stdexcept>', 'runtime_error logic_error invalid_argument out_of_range length_error overflow_error range_error domain_error')
_a('<system_error>', 'error_code error_condition system_error errc generic_category system_category make_error_code')
_a('<tuple>', 'tuple tie apply make_tuple tuple_size tuple_element forward_as_tuple ignore')
_a('<condition_variable>', 'condition_variable condition_variable_any cv_status')
_a('<sstream>', 'ostringstream istringstream stringstream')
_a('<ostream>', 'ostream endl flush')
_a('<istream>', 'istream')
_a('<iostream>', 'cerr cout clog cin')
_a('<fstream>', 'ifstream ofstream fstream')
_a('<limits>', 'numeric_limits')
_a('<numeric>', 'accumulate iota reduce gcd lcm midpoint transform_reduce')
_a('<iterator>', 'back_inserter inserter begin end cbegin cend rbegin rend size ssize data empty distance next prev advance istreambuf_iterator ostreambuf_iterator iterator_traits move_iterator make_move_iterator')
_a('<type_traits>', 'is_same is_same_v remove_cvref_t decay_t enable_if_t conditional_t is_enum_v underlying_type_t is_trivially_copyable_v integral_constant true_type false_type is_constant_evaluated invoke_result_t is_invocable_v')
_a('<initializer_list>', 'initializer_list')
_a('<format>', 'format format_to vformat')
_a('<compare>', 'strong_ordering weak_ordering partial_ordering compare_three_way')
_a('<concepts>', 'same_as convertible_to integral invocable derived_from')
_a('<future>', 'future promise async packaged_task shared_future')
_a('<bit>', 'bit_cast countl_zero popcount endian has_single_bit')
_a('<charconv>', 'from_chars to_chars chars_format')
_a('<cstring>', 'strlen memcpy memcmp memset memmove strcmp strncmp')
_a('<cstdlib>', 'abs getenv exit abort strtol strtoull')
_a('<cmath>', 'floor ceil round lround sqrt pow fabs isnan isfinite')
_a('<latch>', 'latch')
_a('<source_location>', 'source_location')
_a('<typeindex>', 'type_index')
_a('<typeinfo>', 'type_info bad_cast')
_a('<any>', 'any any_cast')
_a('<new>', 'nothrow bad_alloc launder')
_a('<cerrno>', 'errno')
_a('<ratio>', 'ratio milli micro nano')


def std_header(r):
    comps = []
    c = r
    while c is not None and c.kind != K.TRANSLATION_UNIT:
        comps.append(c.spelling)
        c = c.semantic_parent
    comps.reverse()
    if not comps:
        return None
    if comps[0] != 'std':
        f = r.location.file.name if r.location.file is not None else ''
        if is_system(f) and not is_stdlib(f) and comps[0] in T:
            return T[comps[0]]
        return None
    rest = [x for x in comps[1:] if not x.startswith('__') and x]
    for x in rest:
        if x in T:
            return T[x]
        break
    return None


def qt_header(r, qt_dirs):
    c = r
    top = None
    while c is not None and c.kind != K.TRANSLATION_UNIT:
        if c.kind in (K.CLASS_DECL, K.STRUCT_DECL, K.CLASS_TEMPLATE, K.ENUM_DECL, K.TYPEDEF_DECL):
            top = c
        c = c.semantic_parent
    if top is None or not top.spelling.startswith('Q'):
        return None
    for d in qt_dirs:
        if os.path.exists(os.path.join(d, top.spelling)):
            return f'<{top.spelling}>'
    return None
