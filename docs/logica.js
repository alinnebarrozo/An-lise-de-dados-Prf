/* Lógica do painel PRF (sem DOM): decodificação, filtros, indicadores e testes.
   Espelha src/metricas.py e src/analises.py do app Streamlit. */
(function (raiz) {
  "use strict";
  const P = {};

  // ---------------- Decodificação ----------------
  function bytesDe(b64) {
    if (typeof Buffer !== "undefined") { const b = Buffer.from(b64, "base64"); return new Uint8Array(b.buffer, b.byteOffset, b.length); }
    const s = atob(b64), u = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i);
    return u;
  }
  const TIPOS = { uint8: Uint8Array, uint16: Uint16Array, uint32: Uint32Array };
  function coluna([tipo, b64]) {
    const bytes = bytesDe(b64);
    const T = TIPOS[tipo];
    const copia = new Uint8Array(bytes.length); copia.set(bytes);
    return new T(copia.buffer, 0, bytes.length / T.BYTES_PER_ELEMENT);
  }
  P.decodificar = function (j) {
    const oc = {}, ev = {};
    for (const k in j.oc) oc[k] = coluna(j.oc[k]);
    for (const k in j.ev) ev[k] = coluna(j.ev[k]);
    const R = j.rotulos;
    const idx = (lista, v) => lista.indexOf(v);
    return { oc, ev, R, pre: j.pre, nOc: j.n_oc, nEv: j.n_ev,
      COND: idx(R.tenv, "Condutor"), PAS: idx(R.tenv, "Passageiro"), F: 0, M: 1, OBITO: 3, GRAVES: 2 };
  };

  // ---------------- Filtros ----------------
  P.filtroVazio = () => ({ d0: null, d1: null, anos: [], meses: [], ufs: [], muns: [], brs: [], classif: [], tipos: [],
    sexos: [], faixas: [], tenv: [] });
  P.temPessoa = (f) => f.sexos.length + f.faixas.length + f.tenv.length > 0;
  const conj = (a) => (a && a.length ? new Set(a) : null);

  P.aplicar = function (D, f) {
    const o = D.oc, e = D.ev, nO = D.nOc, nE = D.nEv;
    const mo = new Uint8Array(nO);
    const sAno = conj(f.anos), sMes = conj(f.meses), sUf = conj(f.ufs), sMun = conj(f.muns), sBr = conj(f.brs),
      sCl = conj(f.classif), sTp = conj(f.tipos);
    for (let i = 0; i < nO; i++) {
      if (f.d0 !== null && o.data[i] < f.d0) continue;
      if (f.d1 !== null && o.data[i] > f.d1) continue;
      if (sAno && !sAno.has(o.ano[i] + 2024)) continue;
      if (sMes && !sMes.has(o.mes[i])) continue;
      if (sUf && !sUf.has(o.uf[i])) continue;
      if (sMun && !sMun.has(o.mun[i])) continue;
      if (sBr && !sBr.has(o.br[i])) continue;
      if (sCl && !sCl.has(o.classif[i])) continue;
      if (sTp && !sTp.has(o.tipo[i])) continue;
      mo[i] = 1;
    }
    const me = new Uint8Array(nE);
    const sSx = conj(f.sexos), sFx = conj(f.faixas), sTe = conj(f.tenv);
    let nEv = 0;
    for (let i = 0; i < nE; i++) {
      if (!mo[e.oc[i]]) continue;
      if (sSx && !sSx.has(e.sexo[i])) continue;
      if (sFx && !sFx.has(e.faixa[i])) continue;
      if (sTe && !sTe.has(e.tenv[i])) continue;
      me[i] = 1; nEv++;
    }
    let moFinal = mo;
    if (P.temPessoa(f)) {
      moFinal = new Uint8Array(nO);
      for (let i = 0; i < nE; i++) if (me[i]) moFinal[e.oc[i]] = 1;
    }
    let nOc = 0; for (let i = 0; i < nO; i++) nOc += moFinal[i];
    return { mo: moFinal, me, nOc, nEv };
  };

  // ---------------- Estatística ----------------
  P.wilson = function (s, n, z = 1.96) {
    if (!n) return [NaN, NaN];
    const p = s / n, den = 1 + z * z / n, c = (p + z * z / (2 * n)) / den;
    const m = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den;
    return [100 * (c - m), 100 * (c + m)];
  };
  P.rr = function (a, na, b, nb) {
    if (!a || !b) return null;
    const r = (a / na) / (b / nb), ep = Math.sqrt(1 / a - 1 / na + 1 / b - 1 / nb);
    return { rr: r, inf: Math.exp(Math.log(r) - 1.96 * ep), sup: Math.exp(Math.log(r) + 1.96 * ep) };
  };
  function lnGamma(z) {
    const g = 7, c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
      -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
    if (z < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * z)) - lnGamma(1 - z);
    z -= 1; let x = c[0]; for (let i = 1; i < g + 2; i++) x += c[i] / (z + i);
    const t = z + g + 0.5;
    return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
  }
  function gammaQ(a, x) { // função gama incompleta regularizada superior
    if (x <= 0) return 1;
    if (x < a + 1) {
      let soma = 1 / a, termo = soma;
      for (let n = 1; n < 500; n++) { termo *= x / (a + n); soma += termo; if (Math.abs(termo) < Math.abs(soma) * 1e-14) break; }
      return 1 - soma * Math.exp(-x + a * Math.log(x) - lnGamma(a));
    }
    let b = x + 1 - a, c = 1 / 1e-300, d = 1 / b, h = d;
    for (let i = 1; i < 500; i++) {
      const an = -i * (i - a); b += 2;
      d = an * d + b; if (Math.abs(d) < 1e-300) d = 1e-300;
      c = b + an / c; if (Math.abs(c) < 1e-300) c = 1e-300;
      d = 1 / d; const del = d * c; h *= del; if (Math.abs(del - 1) < 1e-14) break;
    }
    return Math.exp(-x + a * Math.log(x) - lnGamma(a)) * h;
  }
  P.efeito = (v) => (v < 0.1 ? "muito pequeno" : v < 0.3 ? "pequeno" : v < 0.5 ? "moderado" : "grande");
  /** tabela: matriz linhas x colunas de contagens */
  P.quiQuadrado = function (tab) {
    let t = tab.filter((l) => l.reduce((a, b) => a + b, 0) > 0);
    if (!t.length) return null;
    const cols = t[0].map((_, j) => t.reduce((a, l) => a + l[j], 0));
    const keep = cols.map((c) => c > 0);
    t = t.map((l) => l.filter((_, j) => keep[j]));
    const r = t.length, k = t[0].length;
    if (r < 2 || k < 2) return null;
    const lin = t.map((l) => l.reduce((a, b) => a + b, 0));
    const col = t[0].map((_, j) => t.reduce((a, l) => a + l[j], 0));
    const n = lin.reduce((a, b) => a + b, 0);
    let q = 0;
    for (let i = 0; i < r; i++) for (let j = 0; j < k; j++) { const ex = lin[i] * col[j] / n; q += (t[i][j] - ex) ** 2 / ex; }
    const gl = (r - 1) * (k - 1);
    const v = Math.sqrt(q / (n * (Math.min(r, k) - 1)));
    return { qui2: q, gl, n, v, p: gammaQ(gl / 2, q / 2), efeito: P.efeito(v) };
  };

  // ---------------- KPIs ----------------
  P.kpis = function (D, mo, me) {
    let nOc = 0, fat = 0, nEv = 0, inf = 0, ob = 0, gr = 0;
    for (let i = 0; i < D.nOc; i++) if (mo[i]) { nOc++; fat += D.oc.fatal[i]; }
    const est = D.ev.estado;
    for (let i = 0; i < D.nEv; i++) if (me[i]) {
      nEv++; const s = est[i];
      if (s !== 255) { inf++; if (s === 3) ob++; if (s >= 2) gr++; }
    }
    return { ocorrencias: nOc, envolvidos: nEv, obitos: ob, fatais: fat, pctFatais: nOc ? 100 * fat / nOc : NaN,
      letalidade: inf ? 100 * ob / inf : NaN, gravidade: inf ? 100 * gr / inf : NaN, informados: inf, graves: gr };
  };

  P.anosPresentes = function (D, mo) {
    const s = new Set(); for (let i = 0; i < D.nOc; i++) if (mo[i]) s.add(D.oc.ano[i] + 2024);
    return [...s].sort();
  };
  P.mesesPorAno = function (D, mo) {
    const m = {}; for (let i = 0; i < D.nOc; i++) if (mo[i]) { const a = D.oc.ano[i] + 2024; (m[a] = m[a] || new Set()).add(D.oc.mes[i]); }
    return m;
  };
  /** Restringe máscaras a um ano e a um conjunto de meses */
  P.restringir = function (D, mo, me, ano, meses) {
    const ms = new Set(meses), o2 = new Uint8Array(D.nOc), e2 = new Uint8Array(D.nEv);
    for (let i = 0; i < D.nOc; i++) if (mo[i] && D.oc.ano[i] + 2024 === ano && ms.has(D.oc.mes[i])) o2[i] = 1;
    for (let i = 0; i < D.nEv; i++) if (me[i] && o2[D.ev.oc[i]]) e2[i] = 1;
    return [o2, e2];
  };
  P.kpisPorAno = function (D, mo, me) {
    return P.anosPresentes(D, mo).map((ano) => {
      const mpa = P.mesesPorAno(D, mo)[ano];
      const [o2, e2] = P.restringir(D, mo, me, ano, [...mpa]);
      return Object.assign({ ano, meses: mpa.size }, P.kpis(D, o2, e2));
    });
  };
  P.compararAnos = function (D, mo, me, a, b) {
    const mpa = P.mesesPorAno(D, mo);
    const meses = [...(mpa[a] || [])].filter((m) => (mpa[b] || new Set()).has(m)).sort((x, y) => x - y);
    const [oa, ea] = P.restringir(D, mo, me, a, meses), [ob, eb] = P.restringir(D, mo, me, b, meses);
    return { a: P.kpis(D, oa, ea), b: P.kpis(D, ob, eb), meses };
  };

  // ---------------- Capítulo 1 ----------------
  P.mensal = function (D, mo, me) {
    const occ = new Map(), ob = new Map();
    const k = (i) => (D.oc.ano[i] + 2024) * 100 + D.oc.mes[i];
    for (let i = 0; i < D.nOc; i++) if (mo[i]) occ.set(k(i), (occ.get(k(i)) || 0) + 1);
    for (let i = 0; i < D.nEv; i++) if (me[i] && D.ev.estado[i] === 3) { const kk = k(D.ev.oc[i]); ob.set(kk, (ob.get(kk) || 0) + 1); }
    return [...occ.keys()].sort((a, b) => a - b).map((kk) => ({ ano: Math.floor(kk / 100), mes: kk % 100, ocorrencias: occ.get(kk), obitos: ob.get(kk) || 0 }));
  };
  P.classifPorAno = function (D, mo) {
    const t = {};
    for (let i = 0; i < D.nOc; i++) if (mo[i] && D.oc.classif[i] !== 255) {
      const a = D.oc.ano[i] + 2024; t[a] = t[a] || [0, 0, 0]; t[a][D.oc.classif[i]]++;
    }
    return t;
  };

  // ---------------- Capítulo 2 ----------------
  P.celulas = function (D, mo) {
    const n = new Map(), f = new Map(), mun = new Map();
    for (let i = 0; i < D.nOc; i++) if (mo[i]) {
      const c = D.oc.cel[i]; if (c === 65535) continue;
      n.set(c, (n.get(c) || 0) + 1); f.set(c, (f.get(c) || 0) + D.oc.fatal[i]);
      let m = mun.get(c); if (!m) { m = new Map(); mun.set(c, m); }
      m.set(D.oc.mun[i], (m.get(D.oc.mun[i]) || 0) + 1);
    }
    return [...n.keys()].map((c) => {
      let melhor = -1, mv = -1; for (const [k, v] of mun.get(c)) if (v > mv) { mv = v; melhor = k; }
      const [nome, uf] = D.R.mun[melhor].split("|");
      return { lat: D.R.cel[c][0], lon: D.R.cel[c][1], ocorrencias: n.get(c), pctFatais: 100 * f.get(c) / n.get(c),
        local: `${titulo(nome)} (${uf})` };
    });
  };
  function titulo(s) { return s.toLowerCase().replace(/(^|\s|-)(\S)/g, (m, a, b) => a + b.toUpperCase()); }
  P.titulo = titulo;
  P.ranking = function (D, mo, coluna, metrica, top = 10, minimo = 200) {
    const n = new Map(), f = new Map(), col = D.oc[coluna];
    for (let i = 0; i < D.nOc; i++) if (mo[i]) { const v = col[i]; n.set(v, (n.get(v) || 0) + 1); f.set(v, (f.get(v) || 0) + D.oc.fatal[i]); }
    let itens = [...n.keys()].map((k) => ({ k, n: n.get(k), pct: 100 * f.get(k) / n.get(k) }));
    if (metrica === "pct") itens = itens.filter((x) => x.n >= minimo);
    itens.sort((a, b) => (metrica === "pct" ? b.pct - a.pct : b.n - a.n));
    return itens.slice(0, top).map((x) => ({
      rotulo: coluna === "uf" ? D.R.uf[x.k] : coluna === "br" ? "BR-" + String(x.k).padStart(3, "0")
        : (([nm, uf]) => `${titulo(nm)} (${uf})`)(D.R.mun[x.k].split("|")),
      valor: metrica === "pct" ? x.pct : x.n, n: x.n }));
  };
  P.calor = function (D, mo, metrica) {
    const n = Array.from({ length: 7 }, () => new Array(24).fill(0)), f = Array.from({ length: 7 }, () => new Array(24).fill(0));
    for (let i = 0; i < D.nOc; i++) if (mo[i] && D.oc.hora[i] !== 255) { n[D.oc.dow[i]][D.oc.hora[i]]++; f[D.oc.dow[i]][D.oc.hora[i]] += D.oc.fatal[i]; }
    if (metrica === "ocorrencias") return n;
    return n.map((l, d) => l.map((v, h) => (v ? 100 * f[d][h] / v : null)));
  };
  P.porFase = function (D, mo) {
    const n = [0, 0, 0, 0], f = [0, 0, 0, 0];
    for (let i = 0; i < D.nOc; i++) if (mo[i] && D.oc.fase[i] !== 255) { n[D.oc.fase[i]]++; f[D.oc.fase[i]] += D.oc.fatal[i]; }
    const tot = n.reduce((a, b) => a + b, 0);
    return D.R.fase.map((nome, j) => ({ fase: nome, ocorrencias: n[j], pctOcorrencias: tot ? 100 * n[j] / tot : 0,
      pctFatais: n[j] ? 100 * f[j] / n[j] : NaN })).filter((x) => x.ocorrencias > 0);
  };
  P.sazonalidade = function (D, mo) {
    const mpa = P.mesesPorAno(D, mo);
    const completos = Object.keys(mpa).map(Number).filter((a) => mpa[a].size === 12).sort();
    if (!completos.length) return { linhas: [], completos };
    const s = new Set(completos), c = new Array(13).fill(0);
    for (let i = 0; i < D.nOc; i++) if (mo[i] && s.has(D.oc.ano[i] + 2024)) c[D.oc.mes[i]]++;
    return { linhas: c.slice(1).map((v, j) => ({ mes: j + 1, media: v / completos.length })), completos };
  };

  // ---------------- Capítulos 3 e 4 ----------------
  /** contagem por (categoria, sexo). fnCat(i) devolve índice/rotulo ou null */
  P.contarPorSexo = function (D, me, fnCat) {
    const t = new Map();
    for (let i = 0; i < D.nEv; i++) if (me[i] && D.ev.sexo[i] !== 255) {
      const c = fnCat(i); if (c === null || c === undefined) continue;
      let l = t.get(c); if (!l) { l = [0, 0]; t.set(c, l); } l[D.ev.sexo[i]]++;
    }
    return t;
  };
  /** % de cada sexo por categoria (cada sexo soma 100) */
  P.pctPorSexo = function (D, me, fnCat, ordem, top) {
    const t = P.contarPorSexo(D, me, fnCat);
    const tot = [0, 0]; for (const l of t.values()) { tot[0] += l[0]; tot[1] += l[1]; }
    let chaves = ordem ? ordem.filter((k) => t.has(k)) : [...t.keys()].sort((a, b) => (t.get(b)[0] + t.get(b)[1]) - (t.get(a)[0] + t.get(a)[1]));
    if (top) chaves = chaves.slice(0, top);
    return chaves.map((k) => ({ cat: k, nF: t.get(k)[0], nM: t.get(k)[1],
      F: tot[0] ? 100 * t.get(k)[0] / tot[0] : 0, M: tot[1] ? 100 * t.get(k)[1] / tot[1] : 0 }));
  };
  /** % de cada sexo dentro de cada papel (cada papel soma 100) */
  P.participacao = function (D, me) {
    const t = P.contarPorSexo(D, me, (i) => D.ev.tenv[i]);
    return D.R.tenv.map((nome, j) => (t.has(j) ? { papel: nome, nF: t.get(j)[0], nM: t.get(j)[1],
      F: 100 * t.get(j)[0] / (t.get(j)[0] + t.get(j)[1]), M: 100 * t.get(j)[1] / (t.get(j)[0] + t.get(j)[1]) } : null))
      .filter(Boolean);
  };
  P.idade = function (D, me) { // condutores com sexo, 14-90
    const c = [new Array(91).fill(0), new Array(91).fill(0)], tot = [0, 0];
    const m = [[], []];
    for (let i = 0; i < D.nEv; i++) if (me[i] && D.ev.tenv[i] === D.COND && D.ev.sexo[i] !== 255) {
      const a = D.ev.idade[i]; if (a === 255) continue;
      m[D.ev.sexo[i]].push(a);
      if (a >= 14 && a <= 90) { c[D.ev.sexo[i]][a]++; tot[D.ev.sexo[i]]++; }
    }
    const med = m.map((l) => { if (!l.length) return NaN; l.sort((x, y) => x - y); const h = l.length >> 1; return l.length % 2 ? l[h] : (l[h - 1] + l[h]) / 2; });
    const x = [], F = [], M = [];
    for (let a = 14; a <= 90; a++) { x.push(a); F.push(tot[0] ? 100 * c[0][a] / tot[0] : 0); M.push(tot[1] ? 100 * c[1][a] / tot[1] : 0); }
    return { x, F, M, mediana: med, tot };
  };
  P.estadoPorPapel = function (D, me) {
    const t = D.R.tenv.map(() => [0, 0, 0, 0]);
    for (let i = 0; i < D.nEv; i++) if (me[i] && D.ev.estado[i] !== 255) t[D.ev.tenv[i]][D.ev.estado[i]]++;
    return D.R.tenv.map((nome, j) => ({ papel: nome, n: t[j] })).filter((x) => x.n.reduce((a, b) => a + b, 0) > 0);
  };
  /** taxas por grupo e sexo (só estado informado) */
  P.taxasPor = function (D, me, fnGrupo) {
    const t = new Map();
    for (let i = 0; i < D.nEv; i++) if (me[i] && D.ev.sexo[i] !== 255 && D.ev.estado[i] !== 255) {
      const g = fnGrupo(i); if (g === null || g === undefined) continue;
      const k = g + "§" + D.ev.sexo[i];
      let r = t.get(k); if (!r) { r = { grupo: g, sexo: D.ev.sexo[i], n: 0, obitos: 0, graves: 0 }; t.set(k, r); }
      r.n++; if (D.ev.estado[i] === 3) r.obitos++; if (D.ev.estado[i] >= 2) r.graves++;
    }
    return [...t.values()].map((r) => {
      const [li, ls] = P.wilson(r.obitos, r.n), [gi, gs] = P.wilson(r.graves, r.n);
      return Object.assign(r, { letalidade: 100 * r.obitos / r.n, gravidade: 100 * r.graves / r.n,
        letInf: li, letSup: ls, gravInf: gi, gravSup: gs });
    });
  };
  /** máscara de condutores com sexo informado a partir de uma máscara de envolvidos */
  P.condutores = function (D, me) {
    const c = new Uint8Array(D.nEv);
    for (let i = 0; i < D.nEv; i++) if (me[i] && D.ev.tenv[i] === D.COND && D.ev.sexo[i] !== 255) c[i] = 1;
    return c;
  };
  P.tabSexoEstado = function (D, mc) {
    const t = [[0, 0, 0, 0], [0, 0, 0, 0]];
    for (let i = 0; i < D.nEv; i++) if (mc[i] && D.ev.estado[i] !== 255) t[D.ev.sexo[i]][D.ev.estado[i]]++;
    return t;
  };
  P.causas = function (D, mc, unico, top = 8) {
    const fn = (i) => { const o = D.ev.oc[i]; if (unico && D.oc.veiculos[o] !== 1) return null; return D.oc.causa[o] === 255 ? null : D.oc.causa[o]; };
    const linhas = P.pctPorSexo(D, mc, fn, null, top);
    const t = P.contarPorSexo(D, mc, fn);
    const tab = [...t.values()].filter((l) => l[0] + l[1] >= 30);
    return { linhas: linhas.map((l) => Object.assign(l, { cat: D.R.causa[l.cat] })), teste: P.quiQuadrado(tab) };
  };

  if (typeof module !== "undefined" && module.exports) module.exports = P; else raiz.PRF = P;
})(typeof window !== "undefined" ? window : globalThis);
