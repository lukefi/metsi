local abs, floor, log, min, pi = math.abs, math.floor, math.log, math.min, math.pi

local crkpk = {
	climbed = {
		{
			2.20965360156452,
			-1.25305667938155,
			-0.49304514839668,
			1.44839436143462,
			-1.73255905590407,
			2.12894867796753,
			-1.74786848717632,
			1.09055366481079
		},
		{
			2.33240369840792,
			-3.26616100355457,
			3.60548511179073,
			-1.9631254327092,
			-0.729874712285328,
			3.10230377562173,
			-3.39277872180019,
			2.0633058239057
		},
		{
			0.983659893064365,
			3.84533586657032,
			-7.75868338419637,
			8.78019094022875,
			-9.48396334037572,
			8.92372883942992,
			-6.4162951441535,
			2.9370964359565
		}
	}
}

local function crkty_ma(d, h)
	local dh = d / (h - 1.3)
	local dl = log(d)
	local hl = log(h)
	return
		1.100553,
		0.8585458,
		0.5442665,
		0.26222 - 0.0016245 * d + 0.010074 * h + 0.06273 * dh - 0.011971 * dh ^ 2 - 0.15496 * hl - 0.45333 / h,
		-0.38383 - 0.0055445 * h - 0.014121 * dl + 0.17496 * hl + 0.62221 / h,
		-0.179 + 0.037116 * dh - 0.12667 * dl + 0.18974 * hl
end

local function crkty_ku(d, h)
	local dh = d / (h - 1.3)
	local dh2 = dh ^ 2
	local dl = log(d)
	local hl = log(h)
	return
		1.0814409,
		0.8409653,
		0.4999158,
		-0.003133 * d + 0.01172 * h + 0.48952 * dh - 0.078688 * dh2 - 0.31296 * dl + 0.13242 * hl - 1.2967 / h,
		-0.0065534 * d + 0.011587 * h - 0.054213 * dh + 0.011557 * dh2 + 0.12598 / h,
		0.084893 - 0.0064871 * d + 0.012711 * h - 0.10287 * dh + 0.026841 * dh2 - 0.01932 * dl
end

local function crkty_ko(d, h)
	local d2 = d ^ 2
	local dh = d / (h - 1.3)
	local dh2 = dh ^ 2
	local dl = log(d)
	local hl = log(h)
	return
		1.084544,
		0.8417135,
		0.4577622,
		0.59848 + 0.011356 * d - 0.49612 * dl + 0.46137 * hl - 0.92116 / dh + 0.25182 / dh2 - 0.00019947 * d2,
		-0.96443 + 0.011401 * d + 0.13870 * dl + 1.5003 / h + 0.57278 / dh - 0.18735 / dh2 - 0.00026 * d2,
		-2.1147 + 0.79368 * dl - 0.51810 * hl + 2.9061 / h + 1.6811 / dh - 0.40778 / dh2 - 0.00011148 * d2
end

local function crkty(spe, d, h)
	if spe == 1 or spe == 7 then
		return crkty_ma(d, h)
	elseif spe == 2 then
		return crkty_ku(d, h)
	else
		-- motin kutsussa näin, alkuperäisessä crk:ssa myös leppä olisi mukana
		return crkty_ko(d, h)
	end
end

local function copysign(x, y)
	if x < 0 then
		return -y
	else
		return y
	end
end

local function crktykd(t1, t4, t7, y1, y4, y7)
	y1 = copysign(min(abs(y1), 0.1), y1)
	y4 = copysign(min(abs(y4), 0.1), y4)
	y7 = copysign(min(abs(y7), 0.1), y7)
	return
		0.9,
		0.6,
		t1 / (t1 + y1) * (t4 + y4) - t4,
		0.3,
		t1 / (t1 + y1) * (t7 + y7) - t7
end

local function crkkd(spe, d, h)
	return crktykd(crkty(spe, d, h))
end

-- [ y(0)  = 0 ]
-- y(x1) = 0
-- y(x2) = y2
-- y(x3) = y3
local function cpoly3(x1, x2, y2, x3, y3)
	local con1 = y2 / (x2 * (x2 - x1))
	local con2 = y3 / (x3 * (x3 - x1))
	local b3 = (con1 - con2) / (x2 - x3)
	local b2 = con1 - b3 * (x1 + x2)
	local b1 = x1 * (x2 * b3 - con1)
	return b1, b2, b3
end

local function xpoly(x)
	local x2 = x * x
	local x3 = x * x2
	local x5 = x2 * x3
	local x8 = x5 * x3
	local x13 = x8 * x5
	local x21 = x13 * x8
	local x34 = x21 * x13
	return x, x2, x3, x5, x8, x13, x21, x34
end

local function crkpoly(c, x)
	local x, x2, x3, x5, x8, x13, x21, x34 = xpoly(x)
	return c[1] * x + c[2] * x2 + c[3] * x3 + c[4] * x5 + c[5] * x8 + c[6] * x13 + c[7] * x21 + c[8] * x34
end

local function crkt(c, h, hx)
	return crkpoly(c, (h - hx) / h)
end

local function intcrkpoly2(c, x)
	local _, x2, x3, x5, x8, x13, _, _ = xpoly(x)
	local c1, c2, c3, c4, c5, c6, c7, c8 = c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8]
	local v = c8 * c8 / 69 * x13
	v = (v + c7 * c8 / 28) * x8
	v = (v + c6 * c8 / 24) * x5
	v = (v + (2 * c5 * c8 + c7 * c7) / 43) * x3
	v = (v + c4 * c8 / 20) * x2
	v = (v + c3 * c8 / 19) * x
	v = (v + c2 * c8 / 18.5) * x
	v = (v + c1 * c8 / 18) * x
	v = (v + c6 * c7 / 17.5) * x5
	v = (v + c5 * c7 / 15) * x3
	v = (v + (2 * c4 * c7 + c6 * c6) / 27) * x2
	v = (v + c3 * c7 * 0.08) * x
	v = (v + c2 * c7 / 12) * x
	v = (v + c1 * c7 / 11.5) * x
	v = (v + c5 * c6 / 11) * x3
	v = (v + c4 * c6 / 9.5) * x2
	v = (v + (2 * c3 * c6 + c5 * c5) / 17) * x
	v = (v + c2 * c6 * 0.125) * x
	v = (v + c1 * c6 / 7.5) * x
	v = (v + c4 * c5 / 7) * x2
	v = (v + c3 * c5 / 6) * x
	v = (v + (2 * c2 * c5 + c4 * c4) / 11) * x
	v = (v + c1 * c5 * 0.2) * x
	v = (v + c3 * c4 / 4.5) * x
	v = (v + c2 * c4 * 0.25) * x
	v = (v + (2 * c1 * c4 + c3 * c3) / 7) * x
	v = (v + c2 * c3 / 3) * x
	v = (v + c1 * c3 * 0.4 + c2 * c2 * 0.2) * x
	v = (v + c1 * c2 * 0.5) * x
	v = (v + c1 * c1 / 3) * x3
	return v
end

local function coeff(spe, d, h)
	local pk = crkpk.climbed[min(spe, 3)]
	local b1, b2, b3 = cpoly3(crkkd(spe, d, h))
	local coef = { pk[1] + b1, pk[2] + b2, pk[3] + b3, pk[4], pk[5], pk[6], pk[7], pk[8] }
	local d20 = d / crkt(coef, h, 1.3)
	for i = 1, 8 do coef[i] = coef[i] * d20 end
	return coef
end

local function arange(a, b, s)
	local i = 1
	local o = {}
	for x = a, b, s do
		o[i] = x
		i = i + 1
	end
	return o
end

local function arangeb(a, b, s)
	local o = arange(a, b, s)
	if o[#o] < b then
		o[#o + 1] = b
	end
	return o
end

local function volume(hkan, height, c)
	local h = arangeb(hkan, height, 0.1)
	local dpiece, vcum = {}, {}
	local height1 = 1 / height
	local int1 = intcrkpoly2(c, (height - h[1]) * height1)
	for i = 1, #h - 1 do
		dpiece[i] = 10 * crkt(c, height, h[i + 1])
		vcum[i] = -pi / 40000 * height * (intcrkpoly2(c, (height - h[i + 1]) * height1) - int1)
	end
	return vcum, dpiece
end

local function argmax(xs)
	local m, j = -math.huge, nil
	for i = 1, #xs do
		local x = xs[i]
		if x > m then
			m, j = x, i
		end
	end
	return j
end

-- dpiece = T[,1]
-- hpiece = T[,2]  (unused)
-- vcum   = T[,3]
-- pcls   = P[,1]
-- ptop   = P[,2]
-- plen   = P[,3]
-- pval   = P[,4]
local function apt(
	spe, d, h,
	pcls, ptop, plen, pval,
	m, div, nas
)
	local div1 = 1 / div
	local n = floor(100 * h * div1 - 1)
	local V, C, A, L = {}, {}, {}, {}
	for i = 1, n do
		V[i] = 0
		C[i] = 0
		A[i] = 0
		L[i] = 0
	end
	local vcum, dpiece = volume(0.1, h, coeff(spe, d, h))
	for i = 1, n do
		for j = 1, m do
			local t = floor(i + plen[j] * div1)
			if t < n and dpiece[t] >= ptop[j] then
				local v = vcum[t] - vcum[i]
				local c = v * pval[j]
				local ctot = c + C[i]
				if ctot > C[t] then
					V[t] = v + V[i]
					C[t] = ctot
					A[t] = pcls[j]
					L[t] = i
				end
			end
		end
	end
	local vol, val = {}, {}
	for i = 1, nas do
		vol[i] = 0
		val[i] = 0
	end
	local maxi = argmax(C)
	while true do
		if maxi < 1 then break end
		local a = A[maxi]
		if a == 0 then break end
		local l = L[maxi]
		vol[a] = vol[a] + V[maxi] - V[l]
		val[a] = val[a] + C[maxi] - C[l]
		maxi = l
	end
	return vol, val
end

local function aptunpack(i, vol, val)
	if vol[i] then
		return vol[i], val[i], aptunpack(i + 1, vol, val)
	end
end

local function aptfunc_fhk(pcls, ptop, plen, pval, m, div, nas)
	return function(spe, d, h)
		return aptunpack(1, apt(spe, d, h, pcls, ptop, plen, pval, m, div, nas))
	end
end

local function aptfunc_lupa(pcls, ptop, plen, pval, m, div, nas)
	return function(spe, d, h)
		return apt(spe, d, h, pcls, ptop, plen, pval, m, div, nas)
	end
end

return {
	aptfunc_fhk = aptfunc_fhk,
	aptfunc_lupa = aptfunc_lupa
}
