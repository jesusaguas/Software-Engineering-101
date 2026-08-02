/**
 * COMMON INTERVIEW QUESTION
 *
 * Design a simplified, in-memory version of the Unix `find` command.
 * Starting from a directory, return all files that match search criteria such
 * as name, extension, or minimum size. Criteria should be composable with
 * logical AND and OR without changing the traversal code.
 */

// =============================================================================
// 1. CLARIFY REQUIREMENTS
// =============================================================================

/**
 * Questions to ask:
 * - Are we searching a real filesystem or an in-memory model?
 * - Do we return files only, or directories too?
 * - Which filters and combinations must we support?
 * - Is traversal recursive, and in what order?
 * - How should invalid filters or malformed trees be handled?
 * - Are symbolic links, permissions, concurrency, and huge trees in scope?
 *
 * Confirmed requirements:
 * 1. Search an in-memory directory tree recursively.
 * 2. Return files only, in deterministic depth-first order.
 * 3. Support exact-name, extension, and minimum-size filters.
 * 4. Support AND and OR combinations of filters.
 * 5. Adding a filter must not require changing the traversal algorithm.
 * 6. Reject invalid entry names, duplicate siblings, and negative sizes.
 *
 * Out of scope:
 * - Real filesystem I/O, symbolic links, permissions, and hidden-file rules.
 * - Glob/regex parsing and shell command-line parsing.
 * - Concurrent mutations while a search is running.
 * - Sorting, pagination, persistence, and distributed search.
 */

// =============================================================================
// 2. IDENTIFY ENTITIES AND RELATIONSHIPS
// =============================================================================

/**
 * FileSystemNode
 *   Shared identity for files and directories.
 *
 * FileEntry
 *   Stores file metadata used by filters: name, size, and modification time.
 *
 * DirectoryEntry
 *   Owns child entries and enforces valid, unique child names.
 *
 * FileFilter
 *   Contract for one matching rule. Concrete filters own their rule data.
 *
 * FindService
 *   Orchestrates traversal and delegates matching to FileFilter.
 *
 * Relationships:
 * - DirectoryEntry contains many FileSystemNodes (Composite structure).
 * - FindService traverses DirectoryEntries.
 * - FindService uses a FileFilter but does not know its concrete type.
 * - AndFilter and OrFilter compose other FileFilters.
 */

// =============================================================================
// 3. DESIGN CLASSES: STATE AND BEHAVIOR
// =============================================================================

/**
 * FileSystemEntry
 *   - name
 *
 * FileEntry extends FileSystemEntry
 *   - sizeInBytes, modifiedAt
 *
 * DirectoryEntry extends FileSystemEntry
 *   - children
 *   + add(entry), getChildren()
 *
 * FileFilter
 *   + matches(file) -> boolean
 *
 * NameFilter / ExtensionFilter / MinSizeFilter
 *   - expected value
 *   + matches(file) -> boolean
 *
 * AndFilter / OrFilter
 *   - child filters
 *   + matches(file) -> boolean
 *
 * FindService
 *   + find(root, filter) -> FileEntry[]
 *
 * Key decisions:
 * - Traversal and matching are separate responsibilities.
 * - Filters use polymorphism, so FindService contains no filter-type switch.
 * - Composition represents the recursive directory tree and filter groups.
 * - A filter is introduced only where the requirements expect variation.
 */

// =============================================================================
// 4. IMPLEMENT THE CORE FLOW
// =============================================================================

abstract class FileSystemNode {
  constructor(readonly name: string) {
    if (name.trim().length === 0 || name.includes("/")) {
      throw new Error(`Invalid entry name: "${name}"`);
    }
  }
}

class FileEntry extends FileSystemNode {
  constructor(
    name: string,
    readonly sizeInBytes: number,
    readonly modifiedAt: Date,
  ) {
    super(name);

    if (sizeInBytes < 0) {
      throw new Error("File size cannot be negative");
    }
  }
}

class DirectoryEntry extends FileSystemNode {
  private readonly children: FileSystemNode[] = [];

  add(entry: FileSystemNode): void {
    if (this.children.some(child => child.name === entry.name)) {
      throw new Error(
        `Entry "${entry.name}" already exists in directory "${this.name}"`,
      );
    }

    this.children.push(entry);
  }

  getChildren(): readonly FileSystemNode[] {
    return [...this.children];
  }
}

interface FileFilter {
  matches(file: FileEntry): boolean;
}

class NameFilter implements FileFilter {
  constructor(private readonly expectedName: string) {}

  matches(file: FileEntry): boolean {
    return file.name === this.expectedName;
  }
}

class ExtensionFilter implements FileFilter {
  private readonly extension: string;

  constructor(extension: string) {
    this.extension = extension.startsWith(".")
      ? extension.slice(1)
      : extension;

    if (this.extension.length === 0) {
      throw new Error("Extension cannot be empty");
    }
  }

  matches(file: FileEntry): boolean {
    const separatorIndex = file.name.lastIndexOf(".");
    const actualExtension = separatorIndex > 0
      ? file.name.slice(separatorIndex + 1)
      : "";

    return actualExtension === this.extension;
  }
}

class MinSizeFilter implements FileFilter {
  constructor(private readonly minimumBytes: number) {
    if (minimumBytes < 0) {
      throw new Error("Minimum size cannot be negative");
    }
  }

  matches(file: FileEntry): boolean {
    return file.sizeInBytes >= this.minimumBytes;
  }
}

class AndFilter implements FileFilter {
  constructor(private readonly filters: readonly FileFilter[]) {
    if (filters.length === 0) {
      throw new Error("AndFilter requires at least one filter");
    }
  }

  matches(file: FileEntry): boolean {
    return this.filters.every(filter => filter.matches(file));
  }
}

class OrFilter implements FileFilter {
  constructor(private readonly filters: readonly FileFilter[]) {
    if (filters.length === 0) {
      throw new Error("OrFilter requires at least one filter");
    }
  }

  matches(file: FileEntry): boolean {
    return this.filters.some(filter => filter.matches(file));
  }
}

class FindService {
  find(root: DirectoryEntry, filter: FileFilter): FileEntry[] {
    const matches: FileEntry[] = [];
    this.visit(root, filter, matches);
    return matches;
  }

  private visit(
    directory: DirectoryEntry,
    filter: FileFilter,
    matches: FileEntry[],
  ): void {
    for (const entry of directory.getChildren()) {
      if (entry instanceof FileEntry) {
        if (filter.matches(entry)) {
          matches.push(entry);
        }
      } else if (entry instanceof DirectoryEntry) {
        this.visit(entry, filter, matches);
      }
    }
  }
}

// -----------------------------------------------------------------------------
// Verification: walk through a concrete scenario.
// -----------------------------------------------------------------------------

const project = new DirectoryEntry("project");
const source = new DirectoryEntry("src");
const tests = new DirectoryEntry("tests");

source.add(new FileEntry("index.ts", 1_200, new Date("2026-01-10")));
source.add(new FileEntry("parser.ts", 8_000, new Date("2026-01-12")));
source.add(new FileEntry("README.md", 3_000, new Date("2026-01-11")));
tests.add(new FileEntry("parser.test.ts", 12_000, new Date("2026-01-13")));
project.add(source);
project.add(tests);

const finder = new FindService();

const largeTypeScriptFiles = new AndFilter([
  new ExtensionFilter("ts"),
  new MinSizeFilter(5_000),
]);

const result = finder.find(project, largeTypeScriptFiles);

console.log(result.map(file => file.name));
// Depth-first result: ["parser.ts", "parser.test.ts"]

const namedFile = finder.find(project, new NameFilter("README.md"));
console.log(namedFile.map(file => file.name));
// Result: ["README.md"]

const typeScriptOrReadme = new OrFilter([
  new ExtensionFilter("ts"),
  new NameFilter("README.md"),
]);

console.log(finder.find(project, typeScriptOrReadme).length);
// Result: 4

/**
 * Edge cases to discuss:
 * - An empty directory returns an empty result.
 * - A file without a dot has no extension.
 * - A leading dot alone does not count as an extension (`.gitignore`).
 * - Duplicate child names and negative sizes are rejected at construction.
 * - A filter that matches nothing returns an empty array.
 *
 * Complexity:
 * - Time: O(n * f), where n is the number of entries visited and f is the
 *   number of leaf filters evaluated for each file.
 * - Space: O(h + m), where h is recursion depth and m is matching files.
 */

// =============================================================================
// 5. HANDLE EXTENSIBILITY FOLLOW-UPS
// =============================================================================

/**
 * Follow-up: "Find files modified after a given date."
 *
 * The traversal does not change. Add one FileFilter implementation:
 */
class ModifiedAfterFilter implements FileFilter {
  constructor(private readonly threshold: Date) {}

  matches(file: FileEntry): boolean {
    return file.modifiedAt.getTime() > this.threshold.getTime();
  }
}

const recentlyModifiedTypeScript = new AndFilter([
  new ExtensionFilter("ts"),
  new ModifiedAfterFilter(new Date("2026-01-11")),
]);

console.log(
  finder.find(project, recentlyModifiedTypeScript).map(file => file.name),
);
// Result: ["parser.ts", "parser.test.ts"]

/**
 * Other likely follow-ups:
 *
 * - NOT expressions:
 *   Add NotFilter wrapping one FileFilter.
 *
 * - Very large trees:
 *   Return an iterator/generator so matches can be streamed instead of stored.
 *   Use an explicit stack if recursion depth may exceed the call stack.
 *
 * - Real Linux filesystem:
 *   Put directory reading and metadata behind a FileSystem abstraction. Handle
 *   I/O errors, permissions, symbolic-link cycles, and links explicitly.
 *
 * - Faster repeated queries:
 *   Build indexes only if measurements justify their memory and update cost.
 *
 * - Directory filters and pruning:
 *   Separate "should return this entry" from "should traverse this directory"
 *   so a directory can fail the result filter without hiding matching children.
 *
 * - Concurrent mutation:
 *   Search a stable snapshot or define synchronization/versioning semantics.
 *
 * Senior-level closing:
 * The initial design stays intentionally in-memory and linear. Its stable
 * boundary is FileFilter; traversal and storage can evolve independently when
 * an actual follow-up requirement justifies the added complexity.
 */
