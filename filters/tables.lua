function Table(tab)
  if not FORMAT:match("docx") then return tab end
 
  -- Create a new table with the same caption, alignment, and other properties
  local new_table = pandoc.Table(
    tab.caption,
    tab.colspecs,
    tab.head,
    tab.bodies,
    tab.foot,
    tab.attr
  )

  for i, _ in ipairs(new_table.colspecs) do
    local is_last = (i == #new_table.colspecs)
    if not is_last then
      table.insert(new_table.colspecs[i], 0.2)
    else
      table.insert(new_table.colspecs[i], 1.0)
    end
  end

  return new_table
end


