import SwiftUI

enum CodeTheme {
    static let background = Color(hex: "#0F1428")
    static let gutter = Color(hex: "#4B5579")
    static let plain = Color(hex: "#E6E9F5")
    static let keyword = Color(hex: "#C792EA")
    static let string = Color(hex: "#C3E88D")
    static let comment = Color(hex: "#6B7499")
    static let number = Color(hex: "#F78C6C")
    static let type = Color(hex: "#FFCB6B")
    static let function = Color(hex: "#82AAFF")
    static let annotation = Color(hex: "#89DDFF")
    static let highlight = Color(hex: "#FBBF24")
}

/// A small, fast, per-line tokenizer for Python, Java, TypeScript, HTML and config files.
enum SyntaxHighlighter {
    enum Kind { case plain, keyword, string, comment, number, type, function, annotation }

    private static let keywords: [String: Set<String>] = [
        "python": ["def", "return", "if", "elif", "else", "for", "while", "in", "not", "and", "or", "is", "None", "True", "False",
                   "class", "self", "import", "from", "as", "lambda", "yield", "break", "continue", "pass", "with", "try", "except",
                   "finally", "raise", "global", "nonlocal", "del", "assert", "async", "await"],
        "java": ["public", "private", "protected", "class", "interface", "enum", "record", "static", "final", "void", "int", "long",
                 "double", "float", "boolean", "char", "byte", "short", "new", "return", "if", "else", "for", "while", "do", "break",
                 "continue", "null", "true", "false", "this", "super", "extends", "implements", "import", "package", "try", "catch",
                 "finally", "throw", "throws", "switch", "case", "default", "var", "instanceof", "abstract", "synchronized", "yield"],
        "typescript": ["const", "let", "var", "function", "return", "if", "else", "for", "while", "of", "in", "new", "class", "extends",
                       "implements", "interface", "type", "export", "import", "from", "as", "public", "private", "protected", "readonly",
                       "constructor", "this", "null", "undefined", "true", "false", "async", "await", "string", "number", "boolean",
                       "void", "any", "unknown", "never", "switch", "case", "default", "break", "continue", "try", "catch", "throw",
                       "typeof", "keyof", "inject", "signal", "computed", "effect", "input", "output", "model"],
    ]

    static func lines(_ code: String, lang: String) -> [AttributedString] {
        code.components(separatedBy: "\n").map { highlight(line: $0, lang: lang) }
    }

    static func highlight(line: String, lang: String) -> AttributedString {
        if lang == "html" { return html(line) }
        var out = AttributedString()
        let kw = keywords[lang == "kotlin" ? "java" : lang] ?? keywords["java"]!
        let chars = Array(line)
        var i = 0
        let commentStart: (Int) -> Bool = { idx in
            if lang == "python" || lang == "yaml" || lang == "properties" { return chars[idx] == "#" }
            return chars[idx] == "/" && idx + 1 < chars.count && (chars[idx + 1] == "/" || chars[idx + 1] == "*")
        }
        func emit(_ s: String, _ k: Kind) {
            var a = AttributedString(s)
            a.foregroundColor = color(k)
            out.append(a)
        }
        while i < chars.count {
            let c = chars[i]
            if commentStart(i) || (c == "*" && line.trimmingCharacters(in: .whitespaces).hasPrefix("*")) {
                emit(String(chars[i...]), .comment)
                break
            }
            if c == "\"" || c == "'" || c == "`" {
                var j = i + 1
                while j < chars.count && chars[j] != c {
                    if chars[j] == "\\" { j += 1 }
                    j += 1
                }
                j = min(j + 1, chars.count)
                emit(String(chars[i..<j]), .string)
                i = j
                continue
            }
            if c == "@" && lang != "python" {
                var j = i + 1
                while j < chars.count && (chars[j].isLetter || chars[j].isNumber || chars[j] == "_" || chars[j] == ".") { j += 1 }
                emit(String(chars[i..<j]), .annotation)
                i = j
                continue
            }
            if c.isNumber {
                var j = i
                while j < chars.count && (chars[j].isNumber || chars[j] == "." || chars[j] == "_" || chars[j] == "L") { j += 1 }
                emit(String(chars[i..<j]), .number)
                i = j
                continue
            }
            if c.isLetter || c == "_" || c == "$" {
                var j = i
                while j < chars.count && (chars[j].isLetter || chars[j].isNumber || chars[j] == "_" || chars[j] == "$") { j += 1 }
                let word = String(chars[i..<j])
                var k = j
                while k < chars.count && chars[k] == " " { k += 1 }
                let isCall = k < chars.count && chars[k] == "("
                let kind: Kind
                if kw.contains(word) {
                    kind = .keyword
                } else if lang == "yaml" || lang == "properties" {
                    kind = (k < chars.count && (chars[k] == ":" || chars[k] == "=")) ? .function : .plain
                } else if isCall {
                    kind = .function
                } else if let f = word.first, f.isUppercase {
                    kind = .type
                } else {
                    kind = .plain
                }
                emit(word, kind)
                i = j
                continue
            }
            emit(String(c), .plain)
            i += 1
        }
        if out.characters.isEmpty { emit(" ", .plain) }
        return out
    }

    private static func html(_ line: String) -> AttributedString {
        var out = AttributedString()
        func emit(_ s: String, _ k: Kind) {
            var a = AttributedString(s)
            a.foregroundColor = color(k)
            out.append(a)
        }
        let chars = Array(line)
        var i = 0
        var inTag = false
        while i < chars.count {
            let c = chars[i]
            if line[line.index(line.startIndex, offsetBy: i)...].hasPrefix("<!--") {
                emit(String(chars[i...]), .comment)
                break
            }
            if c == "{" && i + 1 < chars.count && chars[i + 1] == "{" {
                var j = i + 2
                while j + 1 < chars.count && !(chars[j] == "}" && chars[j + 1] == "}") { j += 1 }
                j = min(j + 2, chars.count)
                emit(String(chars[i..<j]), .function)
                i = j
                continue
            }
            if c == "@" {
                var j = i + 1
                while j < chars.count && chars[j].isLetter { j += 1 }
                emit(String(chars[i..<j]), .keyword)
                i = j
                continue
            }
            if c == "<" {
                var j = i + 1
                if j < chars.count && chars[j] == "/" { j += 1 }
                while j < chars.count && (chars[j].isLetter || chars[j].isNumber || chars[j] == "-") { j += 1 }
                emit(String(chars[i..<j]), .keyword)
                inTag = true
                i = j
                continue
            }
            if c == ">" || (c == "/" && i + 1 < chars.count && chars[i + 1] == ">") {
                emit(String(c), .keyword)
                inTag = c != ">"
                if c == ">" { inTag = false }
                i += 1
                continue
            }
            if c == "\"" {
                var j = i + 1
                while j < chars.count && chars[j] != "\"" { j += 1 }
                j = min(j + 1, chars.count)
                emit(String(chars[i..<j]), .string)
                i = j
                continue
            }
            if inTag && (c.isLetter || c == "[" || c == "(" || c == "*" || c == "#") {
                var j = i
                while j < chars.count && chars[j] != "=" && chars[j] != " " && chars[j] != ">" { j += 1 }
                emit(String(chars[i..<j]), .type)
                i = j
                continue
            }
            emit(String(c), .plain)
            i += 1
        }
        if out.characters.isEmpty { emit(" ", .plain) }
        return out
    }

    static func color(_ k: Kind) -> Color {
        switch k {
        case .plain: return CodeTheme.plain
        case .keyword: return CodeTheme.keyword
        case .string: return CodeTheme.string
        case .comment: return CodeTheme.comment
        case .number: return CodeTheme.number
        case .type: return CodeTheme.type
        case .function: return CodeTheme.function
        case .annotation: return CodeTheme.annotation
        }
    }
}
