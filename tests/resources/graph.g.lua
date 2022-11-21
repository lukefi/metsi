model "tree#grow(pine)" {
	params [[
		f
		d
		h
		site#dd
	]],
	check "spe" *is(1),
	returns [[
		f'
		d'
		h'
	]],
	impl.Lua("grow", "grow_pine")
}

model "tree#grow(spruce)" {
	params [[
		f
		d
		h
		site#dd
	]],
	check "spe" *is(2),
	returns [[
		f'
		d'
		h'
	]],
	impl.Python("tests.test_utils", "grow_dummy")
}
