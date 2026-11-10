-- Permit PDF line breaks in long inline code without changing its text.
local escapes = {
  ["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}",
  ["$"] = "\\$", ["&"] = "\\&", ["#"] = "\\#", ["%"] = "\\%",
  ["_"] = "\\_", ["^"] = "\\textasciicircum{}", ["~"] = "\\textasciitilde{}"
}
local function wrap_code(el)
  if not FORMAT:match("latex") then return nil end
  local text = el.text:gsub("[\\{}$&#%%_^~]", escapes)
  return pandoc.RawInline("latex", "\\texttt{\\protect\\seqsplit{" .. text .. "}}")
end

local function wrap_paragraph(el)
  return el:walk({Code = wrap_code})
end

-- Keep headings and their PDF bookmarks in Pandoc's native representation.
return {{Para = wrap_paragraph, Plain = wrap_paragraph}}
