-- Add an extra linebreak after a header
function Header(header)
  if not FORMAT:match("docx") then return header end

  local new_header = header.content
  table.insert(new_header, pandoc.LineBreak())

  return pandoc.Header(header.level, new_header)
end


-- Add an extra linebreak at the end of a paragraph
function Para(para)
  if not FORMAT:match("docx") then return para end

  local new_para = para.content
  table.insert(new_para, pandoc.LineBreak())

  return pandoc.Para(new_para)
end

