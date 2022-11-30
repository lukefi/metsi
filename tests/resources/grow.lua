local function grow_pine(f, d, h, dd)
	return f-f%100, d+dd/1000, h+dd/2000
end

return {
	grow_pine = grow_pine
}
