/* Capítulos do painel: cada função devolve { html, figs } sem tocar no DOM. */
(function (raiz) {
  "use strict";
  const P = typeof module !== "undefined" ? require("./logica.js") : raiz.PRF;

  // ---------------- Tokens ----------------
  const COR = {
    sup: "#fcfcfb", plano: "#f4f3ee", tinta: "#111315", tinta2: "#4e4f4c", muda: "#8a8983", grade: "#e3e2db",
    eixo: "#c6c5bb", serie: "#2a78d6", apagada: "#cfcec7", F: "#6250d6", M: "#0f8a62",
  };
  const ESTADO = ["#e9a197", "#de6b5c", "#b83a32", "#6e1714"];
  const CLASSIF = ["#e9a197", "#de6b5c", "#6e1714"];
  const SEQ = ["#f3f8fe", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"];
  const FONTE = '"Barlow", system-ui, -apple-system, "Segoe UI", sans-serif';
  const MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
  const MESES_L = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  const DIA_C = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
  const DIA_F = ["às segundas", "às terças", "às quartas", "às quintas", "às sextas", "aos sábados", "aos domingos"];
  const SEXO = ["Feminino", "Masculino"];

  // ---------------- Formatos ----------------
  const n = (v, c = 0) => (v === null || v === undefined || Number.isNaN(v) ? "—"
    : Number(v).toLocaleString("pt-BR", { minimumFractionDigits: c, maximumFractionDigits: c }));
  const pct = (v, c = 1) => (Number.isNaN(v) || v === null || v === undefined ? "—" : n(v, c) + "%");
  const pp = (v, c = 1) => (Number.isNaN(v) ? "—" : (v > 0 ? "+" : v < 0 ? "−" : "±") + n(Math.abs(v), c) + " p.p.");
  const vezes = (v, c = 1) => n(v, c) + "×";
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const corta = (s, k = 46) => (s.length <= k ? s : s.slice(0, k - 1) + "…");
  const pval = (p) => (p < 0.001 ? "p < 0,001" : "p = " + n(p, 3));

  // ---------------- Blocos HTML ----------------
  const B = {
    marco: (km, titulo, pergunta, contexto) => `
      <header class="marco"><div class="km" aria-hidden="true"><small>KM</small><span>${km}</span></div>
      <div><h2>${titulo}</h2><p class="pergunta">${pergunta}</p></div></header>
      <p class="contexto">${contexto}</p>`,
    kpis: (cards) => `<div class="kpis">${cards.map((c) => `<div class="kpi"><div class="rot">${c.rot}</div>
      <div class="val">${c.val}</div>${c.sub ? `<div class="sub">${c.sub}</div>` : ""}${c.delta ? `<div class="delta">${c.delta}</div>` : ""}</div>`).join("")}</div>`,
    leitura: (t, h = "O que os dados revelam") => `<div class="leitura"><h4>${h}</h4>${t}</div>`,
    descoberta: (t) => `<div class="descoberta"><span class="tag">Descoberta</span>${t}</div>`,
    nota: (t) => `<p class="nota">${t}</p>`,
    vazio: () => `<div class="vazio">Nenhum registro no recorte atual. Afrouxe algum filtro ou use <b>Limpar filtros</b>.</div>`,
    grafico: (id, tabela, classe = "") => `<figure class="cartao ${classe}"><div class="grafico" id="${id}"></div>${tabela ? `<details><summary>Ver os números deste gráfico</summary>${tabela}</details>` : ""}</figure>`,
    tabela: (cab, linhas) => `<div class="tab-wrap"><table><thead><tr>${cab.map((c) => `<th>${c}</th>`).join("")}</tr></thead><tbody>${
      linhas.map((l) => `<tr>${l.map((c, j) => `<td${j ? ' class="num"' : ""}>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`,
    seg: (acao, opcoes, atual, rotulo) => `<div class="seg" role="group" aria-label="${rotulo}"><span class="seg-rot">${rotulo}</span>${
      opcoes.map((o) => `<button type="button" class="${o === atual ? "ativo" : ""}" data-acao="${acao}" data-valor="${esc(o)}" aria-pressed="${o === atual}">${o}</button>`).join("")}</div>`,
    legenda: () => `<span class="lg"><i style="background:${COR.F}"></i>Feminino</span> <span class="lg"><i style="background:${COR.M}"></i>Masculino</span>`,
    hip: (cod, titulo, ver, txt, ev) => {
      const s = { confirmada: ["✓", "Confirmada"], nao_confirmada: ["✕", "Não confirmada"], inconclusiva: ["?", "Inconclusiva"] }[ver];
      return `<article class="hip"><div class="topo"><span class="id">${cod}</span><span class="selo ${ver}">${s[0]} ${s[1]}</span></div>
        <h3>${titulo}</h3><p>${txt}</p><div class="ev">${ev}</div></article>`;
    },
  };

  // ---------------- Figuras ----------------
  function base(titulo, sub, altura, extra = {}) {
    const t = `<b>${titulo}</b>` + (sub ? `<br><span style="font-size:12.5px;color:${COR.muda}">${sub}</span>` : "");
    return Object.assign({
      title: { text: t, x: 0, xanchor: "left", y: 0.985, yanchor: "top", font: { size: 16, color: COR.tinta, family: FONTE } },
      font: { family: FONTE, size: 13, color: COR.tinta2 }, paper_bgcolor: COR.sup, plot_bgcolor: COR.sup,
      height: altura, margin: { l: 8, r: 16, t: sub ? 84 : 58, b: 8 }, separators: ",.",
      hoverlabel: { bgcolor: "#fff", bordercolor: COR.eixo, font: { family: FONTE, size: 12, color: COR.tinta } },
      legend: { orientation: "h", yanchor: "bottom", y: 1.0, xanchor: "left", x: 0, font: { size: 12 } },
      xaxis: { showgrid: false, linecolor: COR.eixo, zeroline: false, tickfont: { color: COR.muda }, automargin: true },
      yaxis: { showgrid: true, gridcolor: COR.grade, zeroline: false, tickfont: { color: COR.muda }, automargin: true },
      bargap: 0.25,
    }, extra);
  }
  const ajusta = (l, k, v) => { l[k] = Object.assign({}, l[k], v); return l; };

  const G = {
    evolucao(mensal, titulo, sub) {
      const x = mensal.map((m) => `${m.ano}-${String(m.mes).padStart(2, "0")}-01`);
      const l = base(titulo, sub, 480);
      l.yaxis = Object.assign({}, l.yaxis, { domain: [0.56, 0.94], rangemode: "tozero" });
      l.yaxis2 = Object.assign({}, l.yaxis, { domain: [0, 0.38], rangemode: "tozero" });
      l.xaxis = Object.assign({}, l.xaxis, { anchor: "y", matches: "x2", showticklabels: false, type: "date" });
      l.xaxis2 = Object.assign({}, base("", "", 0).xaxis, { anchor: "y2", type: "date", tickformat: "%b/%y", dtick: "M3" });
      l.showlegend = false; l.hovermode = "x unified";
      l.annotations = [
        { text: "Ocorrências por mês", xref: "paper", yref: "paper", x: 0, y: 0.98, showarrow: false, xanchor: "left", font: { size: 12, color: COR.tinta2 } },
        { text: "Óbitos por mês", xref: "paper", yref: "paper", x: 0, y: 0.43, showarrow: false, xanchor: "left", font: { size: 12, color: COR.tinta2 } }];
      return { data: [
        { type: "scatter", mode: "lines", x, y: mensal.map((m) => m.ocorrencias), line: { color: COR.serie, width: 2 }, name: "Ocorrências", xaxis: "x", yaxis: "y",
          hovertemplate: "<b>%{y:,.0f}</b> ocorrências<extra></extra>" },
        { type: "scatter", mode: "lines", x, y: mensal.map((m) => m.obitos), line: { color: ESTADO[3], width: 2 }, name: "Óbitos", xaxis: "x2", yaxis: "y2",
          hovertemplate: "<b>%{y:,.0f}</b> óbitos<extra></extra>" }], layout: l };
    },
    barras100(linhas, series, pcts, conts, cores, titulo, sub, altura, claras = [0]) {
      const data = series.map((s, j) => ({
        type: "bar", orientation: "h", name: s, y: linhas, x: pcts.map((l) => l[j]),
        marker: { color: cores[j], line: { color: COR.sup, width: 2 } },
        text: pcts.map((l) => (l[j] >= 6 ? pct(l[j]) : "")), textposition: "inside", insidetextanchor: "middle",
        textfont: { color: claras.includes(j) ? COR.tinta : "#fff", size: 12 },
        customdata: conts.map((l) => l[j]),
        hovertemplate: "%{y} · " + s + "<br><b>%{x:.1f}%</b> (%{customdata:,.0f})<extra></extra>" }));
      const l = base(titulo, sub, altura, { barmode: "stack", bargap: 0.35 });
      ajusta(l, "xaxis", { range: [0, 100], ticksuffix: "%" });
      ajusta(l, "yaxis", { autorange: "reversed", showgrid: false });
      l.legend.traceorder = "normal";
      return { data, layout: l };
    },
    ranking(itens, titulo, sub, destaque, formato, altura) {
      const d = itens.slice().reverse(), k = d.length;
      const max = Math.max(...d.map((x) => x.valor), 1);
      return { data: [{ type: "bar", orientation: "h", y: d.map((x) => corta(x.rotulo, 40)), x: d.map((x) => x.valor),
        marker: { color: d.map((_, i) => (!destaque || i >= k - destaque ? COR.serie : COR.apagada)), line: { color: COR.sup, width: 2 } },
        text: d.map((x) => (formato === "pct" ? pct(x.valor) : n(x.valor))), textposition: "outside", cliponaxis: false,
        textfont: { color: COR.tinta2, size: 12 }, customdata: d.map((x) => x.n),
        hovertemplate: "%{y}<br><b>%{text}</b>" + (formato === "pct" ? " · %{customdata:,.0f} ocorrências" : "") + "<extra></extra>" }],
      layout: ajusta(ajusta(base(titulo, sub, altura || Math.max(260, 34 * k + 100), { showlegend: false, margin: { l: 8, r: 48, t: 84, b: 8 } }),
        "xaxis", { showticklabels: false, range: [0, max * 1.2] }), "yaxis", { showgrid: false }) };
    },
    calor(z, titulo, sub, rotulo, fmt) {
      const l = base(titulo, sub, 370);
      ajusta(l, "xaxis", { title: { text: "Hora do dia", font: { size: 12, color: COR.muda } }, dtick: 2 });
      ajusta(l, "yaxis", { autorange: "reversed", showgrid: false });
      return { data: [{ type: "heatmap", z, x: Array.from({ length: 24 }, (_, h) => h), y: DIA_C, xgap: 2, ygap: 2,
        colorscale: SEQ.map((c, i) => [i / (SEQ.length - 1), c]), hoverongaps: false,
        colorbar: { title: { text: rotulo, side: "right" }, thickness: 10, outlinewidth: 0, tickfont: { color: COR.muda } },
        hovertemplate: "%{y} · %{x}h<br><b>%{z:" + fmt + "}</b> " + rotulo + "<extra></extra>" }], layout: l };
    },
    barras(x, y, titulo, sub, rotY, hover, destaque, textos, sufixo = "") {
      const l = base(titulo, sub, 330, { showlegend: false });
      ajusta(l, "yaxis", { title: { text: rotY, font: { size: 12, color: COR.muda } }, rangemode: "tozero", ticksuffix: sufixo });
      return { data: [{ type: "bar", x, y, marker: { color: x.map((_, i) => (!destaque || destaque.includes(i) ? COR.serie : COR.apagada)), line: { color: COR.sup, width: 2 } },
        text: textos, textposition: "outside", cliponaxis: false, textfont: { size: 11, color: COR.tinta2 }, hovertemplate: hover + "<extra></extra>" }], layout: l };
    },
    mapa(cels, titulo, sub) {
      const max = Math.max(...cels.map((c) => c.ocorrencias), 1);
      const fat = cels.map((c) => c.pctFatais).sort((a, b) => a - b);
      const p95 = fat.length ? fat[Math.floor(0.95 * (fat.length - 1))] : 1;
      const ord = cels.slice().sort((a, b) => a.ocorrencias - b.ocorrencias); // grandes por cima
      const l = base(titulo, sub, 600, { showlegend: false, margin: { l: 4, r: 4, t: 84, b: 4 }, dragmode: "pan" });
      l.xaxis = { visible: false, range: [-74.5, -33], fixedrange: false };
      l.yaxis = { visible: false, range: [-34.5, 5.8], scaleanchor: "x", scaleratio: 1 };
      return { data: [{ type: "scattergl", mode: "markers", x: ord.map((c) => c.lon), y: ord.map((c) => c.lat),
        marker: { size: ord.map((c) => 3 + 24 * Math.sqrt(c.ocorrencias / max)), color: ord.map((c) => c.pctFatais), cmin: 0, cmax: p95 || 1,
          colorscale: [[0, "#f3c9c2"], [0.5, "#de6b5c"], [1, "#6e1714"]], opacity: 0.78, line: { color: COR.sup, width: 0.5 },
          colorbar: { title: { text: "% com morte", side: "right" }, thickness: 10, outlinewidth: 0, ticksuffix: "%", len: 0.6 } },
        customdata: ord.map((c) => [c.local, c.ocorrencias, c.pctFatais]),
        hovertemplate: "<b>%{customdata[0]}</b><br>%{customdata[1]:,.0f} ocorrências<br>%{customdata[2]:.1f}% com morte<extra></extra>" }], layout: l };
    },
    barrasSexo(linhas, titulo, sub, rotX, altura) {
      const max = Math.max(...linhas.flatMap((x) => [x.F, x.M]), 1);
      const data = [0, 1].map((s) => ({ type: "bar", orientation: "h", name: SEXO[s], y: linhas.map((x) => corta(String(x.cat))),
        x: linhas.map((x) => (s ? x.M : x.F)), marker: { color: s ? COR.M : COR.F, line: { color: COR.sup, width: 2 } },
        text: linhas.map((x) => pct(s ? x.M : x.F)), textposition: "outside", cliponaxis: false, textfont: { size: 11, color: COR.tinta2 },
        customdata: linhas.map((x) => (s ? x.nM : x.nF)),
        hovertemplate: "%{y}<br>" + SEXO[s] + ": <b>%{x:.1f}%</b> (%{customdata:,.0f})<extra></extra>" }));
      const l = base(titulo, sub, altura || Math.max(300, 54 * linhas.length + 120), { barmode: "group", bargap: 0.3, bargroupgap: 0.05 });
      ajusta(l, "xaxis", { ticksuffix: "%", showgrid: true, gridcolor: COR.grade, range: [0, max * 1.22], title: { text: rotX, font: { size: 12, color: COR.muda } } });
      ajusta(l, "yaxis", { autorange: "reversed", showgrid: false });
      return { data, layout: l };
    },
    linhasSexo(x, F, M, titulo, sub) {
      const l = base(titulo, sub, 370, { hovermode: "x unified" });
      ajusta(l, "xaxis", { title: { text: "Idade", font: { size: 12, color: COR.muda } } });
      ajusta(l, "yaxis", { ticksuffix: "%", rangemode: "tozero", title: { text: "% dos condutores", font: { size: 12, color: COR.muda } } });
      return { data: [["Feminino", F, COR.F], ["Masculino", M, COR.M]].map(([nm, y, c]) => ({ type: "scatter", mode: "lines", name: nm, x, y,
        line: { color: c, width: 2 }, hovertemplate: nm + ": <b>%{y:.2f}%</b><extra></extra>" })), layout: l };
    },
    taxaIC(taxas, ordem, medida, titulo, sub, rotX, nMin = 100) {
      const pos = new Map(ordem.map((g, i) => [g, i]));
      const data = [];
      [0, 1].forEach((s) => {
        [false, true].forEach((vazado) => {
          const d = taxas.filter((t) => t.sexo === s && pos.has(t.grupo) && (t.n < nMin) === vazado);
          if (!d.length) return;
          const v = d.map((t) => t[medida]), inf = d.map((t) => t[medida === "letalidade" ? "letInf" : "gravInf"]),
            sup = d.map((t) => t[medida === "letalidade" ? "letSup" : "gravSup"]);
          data.push({ type: "scatter", mode: "markers", name: SEXO[s], legendgroup: SEXO[s], showlegend: !vazado,
            x: v, y: d.map((t) => pos.get(t.grupo) + (s ? 0.17 : -0.17)),
            marker: { size: 11, color: vazado ? COR.sup : (s ? COR.M : COR.F), line: { color: s ? COR.M : COR.F, width: 2 } },
            error_x: { type: "data", symmetric: false, array: sup.map((x, i) => x - v[i]), arrayminus: inf.map((x, i) => v[i] - x), color: s ? COR.M : COR.F, thickness: 1.5, width: 0 },
            customdata: d.map((t, i) => [t.grupo, t.n, inf[i], sup[i]]),
            hovertemplate: "%{customdata[0]} · " + SEXO[s] + "<br><b>%{x:.2f}%</b> (IC 95%: %{customdata[2]:.2f}–%{customdata[3]:.2f})<br>n = %{customdata[1]:,.0f} condutores<extra></extra>" });
        });
      });
      const l = base(titulo, sub, Math.max(330, 60 * ordem.length + 130));
      ajusta(l, "yaxis", { tickvals: ordem.map((_, i) => i), ticktext: ordem, range: [ordem.length - 0.5, -0.5], showgrid: false });
      ajusta(l, "xaxis", { ticksuffix: "%", showgrid: true, gridcolor: COR.grade, rangemode: "tozero", title: { text: rotX, font: { size: 12, color: COR.muda } } });
      l.shapes = ordem.map((_, i) => (i % 2 ? null : { type: "rect", xref: "paper", x0: 0, x1: 1, y0: i - 0.5, y1: i + 0.5, fillcolor: COR.plano, line: { width: 0 }, layer: "below" })).filter(Boolean);
      return { data, layout: l };
    },
    floresta(reg, titulo, sub) {
      const nome = (t) => t.replace("grupo_veiculo=", "Veículo: ").replace("faixa_etaria=", "Idade: ").replace("fase_dia=", "Fase do dia: ")
        .replace("uso_solo=Sim", "Trecho urbano").replace("tipo_dia=", "").replace("sexo=Masculino", "Sexo: Masculino");
      const d = reg.filter((r) => r.termo !== "(intercepto)").reverse();
      const dest = (r) => r.termo === "sexo=Masculino";
      const l = base(titulo, sub, 34 * d.length + 150, { showlegend: false });
      ajusta(l, "xaxis", { type: "log", showgrid: true, gridcolor: COR.grade, tickvals: [0.25, 0.5, 1, 2, 4, 8], ticktext: ["0,25", "0,5", "1", "2", "4", "8"],
        title: { text: "Razão de chances ajustada (escala log) · 1 = sem diferença", font: { size: 12, color: COR.muda } } });
      ajusta(l, "yaxis", { showgrid: false });
      l.shapes = [{ type: "line", xref: "x", yref: "paper", x0: 1, x1: 1, y0: 0, y1: 1, line: { color: COR.eixo, width: 1.5 } }];
      return { data: [{ type: "scatter", mode: "markers", x: d.map((r) => r.or), y: d.map((r) => nome(r.termo)),
        marker: { symbol: "square", size: d.map((r) => (dest(r) ? 13 : 8)), color: d.map((r) => (dest(r) ? COR.M : COR.tinta2)) },
        error_x: { type: "data", symmetric: false, array: d.map((r) => r.ic_sup - r.or), arrayminus: d.map((r) => r.or - r.ic_inf), color: COR.muda, thickness: 1.5, width: 0 },
        customdata: d.map((r) => [r.ic_inf, r.ic_sup]),
        hovertemplate: "%{y}<br>OR <b>%{x:.2f}</b> (IC 95%: %{customdata[0]:.2f}–%{customdata[1]:.2f})<extra></extra>" }], layout: l };
    },
  };

  // ======================= KM 1 =======================
  function km1(c) {
    const { D, r, S } = c;
    let h = B.marco(1, "O cenário", "Qual é o tamanho do problema nas rodovias federais?",
      "Antes de comparar homens e mulheres, é preciso saber de que volume estamos falando e se ele muda com o tempo. Três grãos não podem ser misturados: <b>ocorrências</b> (acidentes), <b>envolvidos</b> (pessoas) e <b>óbitos</b>.");
    if (!r.nOc || !r.nEv) return { html: h + B.vazio(), figs: [] };
    const k = P.kpis(D, r.mo, r.me), figs = [];
    h += B.kpis([
      { rot: "Ocorrências", val: n(k.ocorrencias), sub: "acidentes registrados pela PRF" },
      { rot: "Pessoas envolvidas", val: n(k.envolvidos), sub: `${n(k.envolvidos / k.ocorrencias, 1)} por ocorrência` },
      { rot: "Óbitos", val: n(k.obitos), sub: "envolvidos com estado = óbito" },
      { rot: "Ocorrências com morte", val: pct(k.pctFatais), sub: k.pctFatais ? `1 a cada ${n(100 / k.pctFatais)} acidentes` : "" },
      { rot: "Taxa de letalidade", val: pct(k.letalidade, 2), sub: "óbitos ÷ envolvidos com estado informado" },
      { rot: "Índice de gravidade", val: pct(k.gravidade), sub: "(óbitos + lesões graves) ÷ estado informado" }]);
    h += B.nota("Óbitos são contados na base de pessoas; a soma de mortos por ocorrência confere com ela (diferença zero no diagnóstico do ETL).");

    const anos = P.anosPresentes(D, r.mo);
    if (anos.length >= 2) {
      const a = anos.includes(S.cmpA) ? S.cmpA : anos[anos.length - 2], b = anos.includes(S.cmpB) ? S.cmpB : anos[anos.length - 1];
      const sel = (id, v) => `<select id="${id}" data-acao="${id}">${anos.map((x) => `<option value="${x}"${x === v ? " selected" : ""}>${x}</option>`).join("")}</select>`;
      h += `<section class="comparar"><div class="comparar-topo"><b>Comparar períodos na mesma janela de meses</b>
        <label for="cmpA">Ano base ${sel("cmpA", a)}</label><label for="cmpB">Comparar com ${sel("cmpB", b)}</label></div>`;
      if (a !== b) {
        const cmp = P.compararAnos(D, r.mo, r.me, a, b);
        if (cmp.meses.length && cmp.a.ocorrencias && cmp.b.ocorrencias) {
          const j = `${MESES[cmp.meses[0] - 1]}–${MESES[cmp.meses[cmp.meses.length - 1] - 1]}`;
          const dv = (x, y) => (y >= x ? "+" : "−") + pct(Math.abs(100 * (y - x) / x)) + ` vs ${a}`;
          h += B.kpis([
            { rot: `Ocorrências (${j})`, val: n(cmp.b.ocorrencias), sub: `${a}: ${n(cmp.a.ocorrencias)}`, delta: dv(cmp.a.ocorrencias, cmp.b.ocorrencias) },
            { rot: `Óbitos (${j})`, val: n(cmp.b.obitos), sub: `${a}: ${n(cmp.a.obitos)}`, delta: cmp.a.obitos ? dv(cmp.a.obitos, cmp.b.obitos) : "" },
            { rot: "Ocorrências com morte", val: pct(cmp.b.pctFatais), sub: `${a}: ${pct(cmp.a.pctFatais)}`, delta: pp(cmp.b.pctFatais - cmp.a.pctFatais, 2) },
            { rot: "Taxa de letalidade", val: pct(cmp.b.letalidade, 2), sub: `${a}: ${pct(cmp.a.letalidade, 2)}`, delta: pp(cmp.b.letalidade - cmp.a.letalidade, 2) }]);
          h += B.nota(`Os dois anos usam só os meses presentes em ambos (${j}), o que evita comparar 2026, que vai até agosto, com um ano inteiro.`);
        } else h += B.nota("Os anos escolhidos não têm meses em comum no recorte atual.");
      } else h += B.nota("Escolha dois anos diferentes para comparar.");
      h += "</section>";
    }

    const mensal = P.mensal(D, r.mo, r.me);
    const media = mensal.reduce((a, m) => a + m.ocorrencias, 0) / mensal.length;
    const pico = mensal.reduce((a, m) => (m.ocorrencias > a.ocorrencias ? m : a), mensal[0]);
    const dp = Math.sqrt(mensal.reduce((a, m) => a + (m.ocorrencias - media) ** 2, 0) / Math.max(mensal.length - 1, 1));
    const cv = 100 * dp / media;
    h += B.grafico("c1_mensal", B.tabela(["Mês", "Ocorrências", "Óbitos"], mensal.map((m) => [`${MESES[m.mes - 1]}/${m.ano}`, n(m.ocorrencias), n(m.obitos)])));
    figs.push(Object.assign({ id: "c1_mensal" }, G.evolucao(mensal, cv < 12 ? "O volume mensal é estável: oscila pouco em torno da média" : "O volume mensal varia bastante ao longo do período",
      `Média de ${n(media)} ocorrências por mês · pico em ${MESES[pico.mes - 1]}/${pico.ano} (${n(pico.ocorrencias)}) · variação típica de ${pct(cv, 0)} em torno da média`)));

    const cl = P.classifPorAno(D, r.mo), anosC = Object.keys(cl);
    const pcts = anosC.map((a) => { const t = cl[a].reduce((x, y) => x + y, 0); return cl[a].map((v) => 100 * v / t); });
    const fat = pcts.map((l) => l[2]);
    const amp = Math.max(...fat) - Math.min(...fat);
    const t1 = anosC.length > 1 ? (amp < 1 ? "A proporção de acidentes fatais quase não muda de um ano para outro" : "A proporção de acidentes fatais muda entre os anos")
      : "Como as ocorrências se dividem por gravidade";
    h += B.grafico("c1_classif", B.tabela(["Ano", ...D.R.classif], anosC.map((a, i) => [a, ...cl[a].map((v, j) => `${n(v)} (${pct(pcts[i][j])})`)])));
    figs.push(Object.assign({ id: "c1_classif" }, G.barras100(anosC, D.R.classif, pcts, anosC.map((a) => cl[a]), CLASSIF, t1,
      `% das ocorrências de cada ano · fatais entre ${pct(Math.min(...fat))} e ${pct(Math.max(...fat))}`, 130 + 48 * anosC.length)));

    let feridas = 0; for (let i = 0; i < D.nOc; i++) if (r.mo[i] && D.oc.classif[i] === 1) feridas++;
    h += B.leitura(`No recorte há <b>${n(k.ocorrencias)} acidentes</b>, com <b>${n(k.envolvidos)} pessoas</b> e <b>${n(k.obitos)} mortes</b>. A maior parte dos acidentes deixa feridos (${pct(100 * feridas / k.ocorrencias)}), e <b>${pct(k.pctFatais)}</b> terminam com pelo menos uma morte. Entre as pessoas com estado físico informado, ${pct(k.letalidade, 2)} morreram e ${pct(k.gravidade)} morreram ou tiveram lesões graves. Como 2026 é parcial, os anos devem ser comparados por taxas ou na mesma janela de meses, nunca pelos totais.`);
    const kpa = P.kpisPorAno(D, r.mo, r.me), pf = kpa.map((x) => x.pctFatais);
    const estavel = kpa.length < 2 || Math.max(...pf) - Math.min(...pf) < 1;
    h += B.descoberta(estavel
      ? `O problema é grande e <b>estável</b>: cerca de 1 em cada ${n(100 / k.pctFatais)} acidentes mata alguém, e essa proporção praticamente não muda ao longo do período. A pergunta deixa de ser “quanto” e passa a ser “onde, quando e com quem”.`
      : `Cerca de 1 em cada ${n(100 / k.pctFatais)} acidentes mata alguém, mas essa proporção <b>muda entre os anos</b> neste recorte, o que pede investigação. A pergunta seguinte é “onde, quando e com quem”.`);
    return { html: h, figs };
  }

  // ======================= KM 2 =======================
  function km2(c) {
    const { D, r, S } = c;
    let h = B.marco(2, "Onde e quando", "Os acidentes se concentram em lugares e horários específicos?",
      "Campanhas e fiscalização têm alcance limitado. Saber onde e quando o risco se concentra indica onde agir primeiro. Aqui separamos <b>volume</b> (quantos acidentes) de <b>letalidade</b> (que parte deles mata), porque os dois nem sempre apontam o mesmo lugar.");
    if (!r.nOc) return { html: h + B.vazio(), figs: [] };
    const figs = [], vol = S.metrica2 !== "% de ocorrências com morte", met = vol ? "n" : "pct";
    h += B.seg("metrica2", ["Volume de ocorrências", "% de ocorrências com morte"], vol ? "Volume de ocorrências" : "% de ocorrências com morte", "Rankings e calendário por");

    const cels = P.celulas(D, r.mo);
    let tm = "Onde ficam os acidentes do recorte";
    if (cels.length >= 10) {
      const o = cels.map((x) => x.ocorrencias).sort((a, b) => b - a), k10 = Math.max(1, Math.round(o.length * 0.1));
      tm = `10% das áreas concentram ${pct(100 * o.slice(0, k10).reduce((a, b) => a + b, 0) / o.reduce((a, b) => a + b, 0), 0)} dos acidentes`;
    }
    const topc = cels.reduce((a, x) => (!a || x.ocorrencias > a.ocorrencias ? x : a), null);
    const uf = P.ranking(D, r.mo, "uf", met, 12);
    let tuf, suf;
    if (vol && uf.length <= 3) { tuf = "Ocorrências por UF no recorte"; suf = "Ocorrências por UF"; }
    else if (vol) { tuf = `Três UFs somam ${pct(100 * uf.slice(0, 3).reduce((a, x) => a + x.valor, 0) / r.nOc, 0)} dos acidentes`; suf = "Ocorrências por UF · 12 maiores"; }
    else { tuf = uf.length ? `${uf[0].rotulo} tem a maior proporção de acidentes fatais` : "UFs"; suf = "% das ocorrências com morte · UFs com 200+ ocorrências"; }
    h += `<div class="duas larga">${B.grafico("c2_mapa", null)}${B.grafico("c2_uf", B.tabela(["UF", vol ? "Ocorrências" : "% com morte"], uf.map((x) => [x.rotulo, vol ? n(x.valor) : pct(x.valor)])))}</div>`;
    figs.push(Object.assign({ id: "c2_mapa" }, G.mapa(cels, tm, "Cada círculo agrega uma área de ~25 km · tamanho = ocorrências · cor = % com morte" + (topc ? ` · maior concentração: ${topc.local}` : "") + " · arraste e use a roda do mouse")));
    figs.push(Object.assign({ id: "c2_uf" }, G.ranking(uf, tuf, suf, 3, vol ? "n" : "pct", 600)));
    h += B.nota("O volume acompanha o tamanho da malha e da frota de cada estado. Sem dado de exposição (km rodados), o ranking por volume não mede risco.");

    const br = P.ranking(D, r.mo, "br", met, 10), mu = P.ranking(D, r.mo, "mun", met, 10);
    let tbr, sbr;
    if (vol && br.length) {
      const folga = br.length > 2 && br[1].valor >= 1.5 * br[2].valor;
      tbr = br.length > 1 ? `${br[0].rotulo} e ${br[1].rotulo} lideram${folga ? " com folga" : ""}` : `${br[0].rotulo} lidera`;
      sbr = `Ocorrências por rodovia · ${br[0].rotulo} concentra ${pct(100 * br[0].valor / r.nOc)} do recorte`;
    } else { tbr = "Rodovias com menos volume podem ser as mais letais"; sbr = "% das ocorrências com morte · rodovias com 200+ ocorrências"; }
    const tmu = vol && mu.length ? `${mu[0].rotulo} lidera, com ${n(mu[0].valor)} ocorrências` : mu.length ? "Municípios onde os acidentes mais matam" : "Sem municípios com 200+ ocorrências";
    const tb = (l) => B.tabela(["Local", vol ? "Ocorrências" : "% com morte"], l.map((x) => [x.rotulo, vol ? n(x.valor) : pct(x.valor)]));
    h += `<div class="duas">${B.grafico("c2_br", tb(br))}${B.grafico("c2_mun", tb(mu))}</div>`;
    figs.push(Object.assign({ id: "c2_br" }, G.ranking(br, tbr, sbr, 2, vol ? "n" : "pct")));
    figs.push(Object.assign({ id: "c2_mun" }, G.ranking(mu, tmu, vol ? "Ocorrências por município" : "% com morte · municípios com 200+ ocorrências", 3, vol ? "n" : "pct")));

    const z = P.calor(D, r.mo, vol ? "ocorrencias" : "pct");
    let tc, sc;
    if (vol) {
      let pd = 0, ph = 0, mx = -1, tot = 0, mad = 0;
      z.forEach((l, d) => l.forEach((v, hh) => { tot += v; if (hh <= 5) mad += v; if (v > mx) { mx = v; pd = d; ph = hh; } }));
      const calma = mad / (7 * 6) < 0.5 * tot / (7 * 24);
      tc = `O pico de acidentes é ${DIA_F[pd]}, às ${ph}h${calma ? "; as madrugadas têm pouco movimento" : ""}`; sc = "Ocorrências por dia da semana e hora de início";
    } else {
      const med = (h0, h1) => { const v = z.flatMap((l) => l.slice(h0, h1 + 1)).filter((x) => x !== null); return v.reduce((a, b) => a + b, 0) / v.length; };
      const razao = med(0, 5) / med(9, 16);
      tc = razao > 1 ? `De madrugada há menos acidentes, mas eles matam ${n(razao, 1)}× mais` : "Letalidade por dia e hora"; sc = "% das ocorrências com morte por dia e hora (0h–5h vs 9h–16h)";
    }
    h += B.grafico("c2_calor", B.tabela(["Dia", ...Array.from({ length: 24 }, (_, x) => x + "h")], z.map((l, d) => [DIA_C[d], ...l.map((v) => (v === null ? "—" : vol ? n(v) : n(v, 1)))])));
    figs.push(Object.assign({ id: "c2_calor" }, G.calor(z, tc, sc, vol ? "ocorrências" : "% com morte", vol ? ",.0f" : ".1f")));

    const fase = P.porFase(D, r.mo), saz = P.sazonalidade(D, r.mo);
    h += `<div class="duas">`;
    if (fase.length && Math.min(...fase.map((x) => x.ocorrencias)) >= 100 && Math.min(...fase.map((x) => x.pctFatais)) > 0) {
      const mx = fase.reduce((a, x) => (x.pctFatais > a.pctFatais ? x : a)), mn = fase.reduce((a, x) => (x.pctFatais < a.pctFatais ? x : a));
      const razao = mx.pctFatais / mn.pctFatais;
      h += B.grafico("c2_fase", B.tabela(["Fase", "Ocorrências", "% do total", "% com morte"], fase.map((x) => [x.fase, n(x.ocorrencias), pct(x.pctOcorrencias), pct(x.pctFatais)])));
      figs.push(Object.assign({ id: "c2_fase" }, G.barras(fase.map((x) => x.fase), fase.map((x) => x.pctFatais),
        ["Plena Noite", "Amanhecer"].includes(mx.fase) ? `Acidentes à noite e ao amanhecer matam até ${n(razao, 1)}× mais que os de pleno dia` : `A proporção de acidentes com morte varia até ${n(razao, 1)}× entre as fases do dia`,
        `% das ocorrências com morte por fase do dia · maior em: ${mx.fase}`, "% com morte", "%{x}: <b>%{y:.1f}%</b> com morte",
        fase.map((x, i) => (["Plena Noite", "Amanhecer"].includes(x.fase) ? i : -1)).filter((i) => i >= 0), fase.map((x) => pct(x.pctFatais)), "%")));
    } else h += `<div class="cartao">${B.nota("Poucas ocorrências por fase do dia neste recorte para comparar a letalidade com segurança.")}</div>`;
    if (saz.linhas.length) {
      const mx = saz.linhas.reduce((a, x) => (x.media > a.media ? x : a)), mn = saz.linhas.reduce((a, x) => (x.media < a.media ? x : a));
      h += B.grafico("c2_saz", B.tabela(["Mês", "Média de ocorrências"], saz.linhas.map((x) => [MESES[x.mes - 1], n(x.media)])));
      figs.push(Object.assign({ id: "c2_saz" }, G.barras(saz.linhas.map((x) => MESES[x.mes - 1]), saz.linhas.map((x) => x.media),
        `${MESES_L[mx.mes - 1][0].toUpperCase() + MESES_L[mx.mes - 1].slice(1)} é o mês mais carregado; ${MESES_L[mn.mes - 1]}, o mais leve`,
        `Média de ocorrências por mês · anos completos no recorte: ${saz.completos.join(", ")}`, "ocorrências/mês", "%{x}: <b>%{y:,.0f}</b> em média", [mx.mes - 1])));
    } else h += `<div class="cartao">${B.nota("A sazonalidade usa só anos completos, e o recorte atual não tem nenhum ano com 12 meses.")}</div>`;
    h += `</div>`;

    const fx = Object.fromEntries(fase.map((x) => [x.fase, x]));
    if (fx["Pleno dia"] && fx["Plena Noite"] && fx["Plena Noite"].pctFatais > fx["Pleno dia"].pctFatais && fx["Plena Noite"].ocorrencias >= 100) {
      h += B.leitura(`O volume se concentra nos estados e rodovias de maior tráfego e cresce nos fins de tarde e fins de semana. Já a <b>letalidade</b> segue outra lógica: à noite acontecem ${pct(fx["Plena Noite"].pctOcorrencias, 0)} dos acidentes, mas ${pct(fx["Plena Noite"].pctFatais)} deles têm morte, contra ${pct(fx["Pleno dia"].pctFatais)} durante o dia. Menos movimento, menos visibilidade e mais velocidade são explicações plausíveis, mas não estão medidas nesta base.`);
      h += B.descoberta("<b>Onde e quando há mais acidentes não é onde e quando eles mais matam.</b> O volume aponta para os grandes corredores e o horário de pico; a letalidade aponta para a noite e a madrugada. Isso será decisivo no KM 4: se homens e mulheres dirigem em horários diferentes, parte da diferença de gravidade pode vir do horário, e não do sexo.");
    }
    return { html: h, figs };
  }

  // ======================= KM 3 =======================
  function km3(c) {
    const { D, r, pre, f } = c;
    let h = B.marco(3, "Quem se envolve", "Qual é o perfil das pessoas envolvidas, e onde estão as mulheres?",
      "A crença popular fala de quem <b>dirige</b>. Mas a base da PRF registra condutores, passageiros, pedestres e testemunhas. Antes de comparar homens e mulheres, é preciso ver em que papel cada um aparece, porque isso muda a leitura de qualquer indicador. " + B.legenda());
    if (!r.nEv) return { html: h + B.vazio(), figs: [] };
    const figs = [], part = P.participacao(D, r.me);
    let semSexo = 0; for (let i = 0; i < D.nEv; i++) if (r.me[i] && D.ev.sexo[i] === 255) semSexo++;
    const cards = [{ rot: "Envolvidos com sexo informado", val: pct(100 * (1 - semSexo / r.nEv)), sub: `${n(semSexo)} sem informação ficam fora dos %` }];
    const pl = { Condutor: "condutores", Passageiro: "passageiros", Pedestre: "pedestres" };
    part.filter((p) => pl[p.papel]).forEach((p) => cards.push({ rot: `Mulheres entre ${pl[p.papel]}`, val: pct(p.F), sub: `${n(p.nF)} de ${n(p.nF + p.nM)}` }));
    h += B.kpis(cards);
    const pc = part.find((p) => p.papel === "Condutor"), pp_ = part.find((p) => p.papel === "Passageiro");
    if (part.length) {
      h += B.grafico("c3_papel", B.tabela(["Papel", "Feminino", "Masculino"], part.map((p) => [p.papel, `${n(p.nF)} (${pct(p.F)})`, `${n(p.nM)} (${pct(p.M)})`])));
      figs.push(Object.assign({ id: "c3_papel" }, G.barras100(part.map((p) => p.papel), SEXO, part.map((p) => [p.F, p.M]), part.map((p) => [p.nF, p.nM]), [COR.F, COR.M],
        pc && pp_ ? `Mulheres são ${pct(pc.F, 0)} de quem dirigia, mas ${pct(pp_.F, 0)} de quem estava de carona` : "Participação de cada sexo por papel na ocorrência",
        "% de cada papel · só envolvidos com sexo informado", 120 + 50 * part.length, [])));
    }
    h += `<div class="duas">`;
    const id = P.idade(D, r.me);
    if (id.tot[0] && id.tot[1]) {
      const suav = (y) => y.map((_, i) => { const w = y.slice(Math.max(0, i - 1), i + 2); return w.reduce((a, b) => a + b, 0) / w.length; });
      h += B.grafico("c3_idade", B.tabela(["Idade", "Feminino (%)", "Masculino (%)"], id.x.map((a, i) => [a, n(id.F[i], 2), n(id.M[i], 2)])));
      figs.push(Object.assign({ id: "c3_idade" }, G.linhasSexo(id.x, suav(id.F), suav(id.M),
        `Condutoras são um pouco mais jovens: mediana de ${n(id.mediana[0])} anos contra ${n(id.mediana[1])}`,
        "% dos condutores de cada sexo por idade (média móvel de 3 anos) · 14 a 90 anos")));
    } else h += `<div class="cartao">${B.nota("Distribuição de idade indisponível: o recorte não tem condutores dos dois sexos.")}</div>`;
    const mc = P.condutores(D, r.me);
    const veic = P.pctPorSexo(D, mc, (i) => (D.ev.veic[i] === 6 ? null : D.R.veic[D.ev.veic[i]]), D.R.veic.slice(0, 6));
    if (veic.length && id.tot[0] && id.tot[1]) {
      const g = (k) => veic.find((x) => x.cat === k) || { F: 0, M: 0 };
      h += B.grafico("c3_veic", B.tabela(["Veículo", "Feminino", "Masculino"], veic.map((x) => [x.cat, `${n(x.nF)} (${pct(x.F)})`, `${n(x.nM)} (${pct(x.M)})`])));
      figs.push(Object.assign({ id: "c3_veic" }, G.barrasSexo(veic, `Elas dirigiam sobretudo automóveis (${pct(g("Automóvel").F, 0)}); caminhões são ${pct(g("Caminhão").M, 0)} dos casos deles e ${pct(g("Caminhão").F, 0)} dos delas`,
        "% dos condutores de cada sexo por tipo de veículo", "% dos condutores")));
    }
    h += `</div>`;
    if (id.tot[0] + id.tot[1]) h += B.nota(`${n(pre.idade_padrao)} condutores com idade 0 no dado original foram tratados como idade não informada: é um valor padrão de preenchimento, não idade real.`);

    const est = P.estadoPorPapel(D, r.me).filter((x) => x.papel !== "Testemunha");
    if (est.length) {
      const pcs = est.map((x) => { const t = x.n.reduce((a, b) => a + b, 0); return x.n.map((v) => 100 * v / t); });
      const ped = est.findIndex((x) => x.papel === "Pedestre");
      h += B.grafico("c3_estado", B.tabela(["Papel", ...D.R.estado], est.map((x, i) => [x.papel, ...x.n.map((v, j) => `${n(v)} (${pct(pcs[i][j])})`)])));
      figs.push(Object.assign({ id: "c3_estado" }, G.barras100(est.map((x) => x.papel), D.R.estado, pcs, est.map((x) => x.n), ESTADO,
        ped >= 0 ? `Pedestres são o grupo mais vulnerável: ${pct(pcs[ped][3])} morrem` : "Estado físico após o acidente no recorte",
        "Estado físico após o acidente, % de cada papel · só estado informado", 120 + 50 * est.length)));
    }
    // ponte
    const todos = P.taxasPor(D, r.me, () => "Todos os envolvidos"), cond = P.taxasPor(D, mc, () => "Somente condutores");
    const lin = [...todos, ...cond];
    if (lin.length === 4) {
      const get = (g, s) => lin.find((x) => x.grupo === g && x.sexo === s).letalidade;
      const linhas = ["Todos os envolvidos", "Somente condutores"].map((g) => ({ cat: g, F: get(g, 0), M: get(g, 1), nF: lin.find((x) => x.grupo === g && x.sexo === 0).n, nM: lin.find((x) => x.grupo === g && x.sexo === 1).n }));
      h += B.grafico("c3_ponte", B.tabela(["Grupo", "Letalidade F", "Letalidade M"], linhas.map((x) => [x.cat, pct(x.F, 2), pct(x.M, 2)])));
      figs.push(Object.assign({ id: "c3_ponte" }, G.barrasSexo(linhas, "Filtrar só quem dirigia muda o tamanho da diferença", "Taxa de letalidade por sexo · todos os envolvidos vs. somente condutores", "% que morreram", 290)));
      h += B.leitura(`Entre todos os envolvidos, a letalidade é de ${pct(linhas[0].F, 2)} para mulheres e ${pct(linhas[0].M, 2)} para homens. Entre os <b>condutores</b>, passa a ${pct(linhas[1].F, 2)} e ${pct(linhas[1].M, 2)}. A diferença muda porque as mulheres aparecem muito mais como passageiras, um papel com risco próprio. Misturar papéis misturaria quem dirigia com quem estava de carona.`);
    }
    if (pc && pp_ && pc.F < 50 && pp_.F > 50 && !f.sexos.length)
      h += B.descoberta("As mulheres são <b>minoria entre quem dirigia</b> e maioria entre passageiros. Também dirigiam <b>outros veículos</b>: mais automóveis, quase nenhum caminhão. Esses dois fatos obrigam o próximo passo a comparar só condutores e a <b>controlar o tipo de veículo</b>; do contrário, estaríamos comparando um carro de passeio com uma carreta.");
    else h += B.nota("A descoberta deste capítulo compara os dois sexos em todos os papéis. Para vê-la, retire os filtros de sexo e de tipo de envolvido.");
    return { html: h, figs };
  }

  // ======================= KM 4 =======================
  const ESTRATOS = ["Tipo de veículo", "Faixa etária", "Fase do dia", "Trecho urbano/rural"];
  const CARAC = { "Tipo de acidente": ["tipo", null, 8], "Fase do dia": ["fase", "ord", null], "Dia da semana": ["dow", "ord", null],
    "Condição meteorológica": ["cond", null, 6], "Traçado da via": ["tracado", null, 6], "Tipo de pista": ["pista", null, null] };

  function km4(c) {
    const { D, S, pre, f } = c;
    let h = B.marco(4, "Investigando as diferenças", "A diferença entre condutoras e condutores se sustenta quando olhamos de perto?",
      "Aqui a comparação é feita só entre <b>condutores</b> com sexo informado, e todo percentual usa como denominador os condutores de cada sexo. Isso não é taxa de risco: a base não diz quantos homens e mulheres dirigem nem quanto. Cada diferença vem com intervalo de confiança de 95% e com uma medida de <b>tamanho do efeito</b>, porque, com centenas de milhares de registros, quase tudo dá “significativo”. " + B.legenda());
    const f2 = Object.assign({}, f, { sexos: [], tenv: [D.COND] });
    const r = c.aplicarCom(f2), mc = P.condutores(D, r.me);
    const avisos = [];
    if (f.sexos.length) avisos.push("o filtro de sexo não se aplica aqui, porque este capítulo compara os dois");
    if (f.tenv.length && !(f.tenv.length === 1 && f.tenv[0] === D.COND)) avisos.push("o tipo de envolvido é sempre Condutor");
    if (avisos.length) h += B.nota("Neste capítulo, " + avisos.join("; ") + ".");
    const tab = P.tabSexoEstado(D, mc);
    const nF = tab[0].reduce((a, b) => a + b, 0), nM = tab[1].reduce((a, b) => a + b, 0);
    if (!nF || !nM) return { html: h + B.vazio(), figs: [] };
    const figs = [], teste = P.quiQuadrado(tab);
    const tx = P.taxasPor(D, mc, () => "t"), fem = tx.find((x) => x.sexo === 0), mas = tx.find((x) => x.sexo === 1);
    const rr = P.rr(mas.obitos, mas.n, fem.obitos, fem.n);
    h += B.kpis([
      { rot: "Letalidade · condutoras", val: pct(fem.letalidade, 2), sub: `IC 95%: ${pct(fem.letInf, 2)} a ${pct(fem.letSup, 2)} · n = ${n(fem.n)}` },
      { rot: "Letalidade · condutores", val: pct(mas.letalidade, 2), sub: `IC 95%: ${pct(mas.letInf, 2)} a ${pct(mas.letSup, 2)} · n = ${n(mas.n)}` },
      { rot: "Risco relativo de óbito (H ÷ M)", val: rr ? vezes(rr.rr, 2) : "—", sub: rr ? `IC 95%: ${n(rr.inf, 2)} a ${n(rr.sup, 2)}` : "sem óbitos femininos no recorte" },
      { rot: "Força da associação sexo × estado físico", val: teste ? n(teste.v, 3) : "—", sub: teste ? `V de Cramér · efeito ${teste.efeito} · ${pval(teste.p)}` : "" }]);
    const pcs = tab.map((l) => { const t = l.reduce((a, b) => a + b, 0); return l.map((v) => 100 * v / t); });
    h += B.grafico("c4_estado", B.tabela(["Sexo", ...D.R.estado], tab.map((l, s) => [SEXO[s], ...l.map((v, j) => `${n(v)} (${pct(pcs[s][j])})`)])));
    figs.push(Object.assign({ id: "c4_estado" }, G.barras100(SEXO, D.R.estado, pcs, tab, ESTADO,
      pcs[0][0] < pcs[1][0] && pcs[0][3] < pcs[1][3] ? "Condutoras saem ilesas com menos frequência, mas morrem com menos frequência" : "Estado físico após o acidente, por sexo do condutor",
      "% dos condutores de cada sexo com estado físico informado", 240)));

    // estratificação
    h += `<h3 class="sub">A diferença persiste dentro de grupos comparáveis?</h3>`;
    h += B.nota("Se a diferença viesse só do veículo, da idade ou do horário, ela desapareceria dentro de cada grupo. Escolha a variável de controle e a medida.");
    h += `<div class="controles">${B.seg("estrato", ESTRATOS, S.estrato, "Controlar por")}${B.seg("medida", ["Letalidade", "Índice de gravidade"], S.medida, "Medida")}</div>`;
    const fnG = { "Tipo de veículo": [(i) => (D.ev.veic[i] === 6 ? null : D.R.veic[D.ev.veic[i]]), D.R.veic.slice(0, 6)],
      "Faixa etária": [(i) => (D.ev.faixa[i] === 255 ? null : D.R.faixa[D.ev.faixa[i]]), D.R.faixa],
      "Fase do dia": [(i) => (D.oc.fase[D.ev.oc[i]] === 255 ? null : D.R.fase[D.oc.fase[D.ev.oc[i]]]), D.R.fase],
      "Trecho urbano/rural": [(i) => (D.oc.uso[D.ev.oc[i]] ? "Urbano" : "Rural"), ["Urbano", "Rural"]] }[S.estrato];
    const medida = S.medida === "Letalidade" ? "letalidade" : "gravidade";
    const estr = P.taxasPor(D, mc, fnG[0]);
    const ordem = fnG[1].filter((g) => estr.some((x) => x.grupo === g));
    let val = 0, mm = 0;
    ordem.forEach((g) => { const a = estr.find((x) => x.grupo === g && x.sexo === 0), b = estr.find((x) => x.grupo === g && x.sexo === 1);
      if (a && b && a.n >= 100 && b.n >= 100) { val++; if (b[medida] > a[medida]) mm++; } });
    h += B.grafico("c4_estr", B.tabela(["Grupo", "Sexo", "n", S.medida, "IC 95%"], ordem.flatMap((g) => [0, 1].map((s) => estr.find((x) => x.grupo === g && x.sexo === s)).filter(Boolean)
      .map((x) => [x.grupo, SEXO[x.sexo], n(x.n), pct(x[medida], 2), medida === "letalidade" ? `${n(x.letInf, 2)}–${n(x.letSup, 2)}` : `${n(x.gravInf, 2)}–${n(x.gravSup, 2)}`]))));
    figs.push(Object.assign({ id: "c4_estr" }, G.taxaIC(estr, ordem, medida, `Em ${mm} de ${val} grupos com dados suficientes, a ${S.medida.toLowerCase()} dos homens é maior`,
      `${S.medida} por ${S.estrato.toLowerCase()} e sexo · barras = IC 95% · círculo vazado = menos de 100 condutores (evidência fraca)`, `${S.medida} (%)`)));

    // regressão (base completa)
    const reg = pre.regressao, lin = reg.find((x) => x.termo === "sexo=Masculino"), br = pre.or_bruta;
    h += `<h3 class="sub">Controlando tudo ao mesmo tempo: regressão logística</h3>`;
    h += B.grafico("c4_reg", B.tabela(["Termo", "OR", "IC 95%", "p"], reg.filter((x) => x.termo !== "(intercepto)").map((x) => [x.termo, n(x.or, 2), `${n(x.ic_inf, 2)}–${n(x.ic_sup, 2)}`, pval(x.p)])));
    figs.push(Object.assign({ id: "c4_reg" }, G.floresta(reg, `Mesmo com os controles, a chance de óbito de um condutor homem é ${n(lin.or, 2)}× a de uma condutora`,
      `Desfecho: óbito · ajustado por veículo, faixa etária, fase do dia, trecho urbano/rural e dia da semana · n = ${n(pre.reg_n)} condutores, ${n(pre.reg_eventos)} óbitos · base completa`)));
    h += B.leitura(`Sem ajuste, a razão de chances de óbito (homens ÷ mulheres) é <b>${n(br.or, 2)}</b>. Com ajuste, cai para <b>${n(lin.or, 2)}</b> (IC 95%: ${n(lin.ic_inf, 2)} a ${n(lin.ic_sup, 2)}). Ou seja, parte da diferença vinha do veículo, da idade e do horário, mas a maior parte permanece. Os outros fatores do modelo também ajudam a calibrar a leitura: dirigir moto ou bicicleta, de madrugada, em trecho rural e com 60 anos ou mais pesam muito mais do que o sexo.`, "Como ler o modelo");
    h += B.nota("O modelo usa a base completa, sem filtros, para ter estabilidade. Ele mede associação, não causa: faltam variáveis como velocidade, uso de cinto/capacete e km rodados.");

    // causas
    h += `<h3 class="sub">Quais causas aparecem em cada perfil?</h3>`;
    h += `<label class="toggle"><input type="checkbox" id="unico" data-acao="unico"${S.unico ? " checked" : ""}> Só acidentes com um único veículo (quando não há dúvida sobre quem dirigia)</label>`;
    const cs = P.causas(D, mc, S.unico);
    if (cs.linhas.length) {
      const dif = cs.linhas.map((x) => x.M - x.F);
      const iM = dif.indexOf(Math.max(...dif)), iF = dif.indexOf(Math.min(...dif));
      h += B.grafico("c4_causas", B.tabela(["Causa", "Feminino", "Masculino"], cs.linhas.map((x) => [x.cat, `${n(x.nF)} (${pct(x.F)})`, `${n(x.nM)} (${pct(x.M)})`])));
      figs.push(Object.assign({ id: "c4_causas" }, G.barrasSexo(cs.linhas, `Entre homens pesam mais “${cs.linhas[iM].cat.toLowerCase()}”; entre mulheres, “${cs.linhas[iF].cat.toLowerCase()}”`,
        "% dos condutores de cada sexo por causa principal · " + (S.unico ? "acidentes com 1 veículo" : "todos os acidentes (a causa é da ocorrência, não do condutor)") + (cs.teste ? ` · V de Cramér = ${n(cs.teste.v, 3)} (${cs.teste.efeito})` : ""), "% dos condutores")));
      if (!S.unico) h += B.nota("Num acidente com dois veículos, a mesma causa aparece para os dois motoristas. Por isso o recorte de veículo único é o mais confiável para ligar causa a perfil.");
    }

    // características
    h += `<h3 class="sub">Em que circunstâncias cada um se acidenta?</h3>`;
    h += `<label class="sel" for="carac">Característica da ocorrência <select id="carac" data-acao="carac">${Object.keys(CARAC).map((k) => `<option${k === S.carac ? " selected" : ""}>${k}</option>`).join("")}</select></label>`;
    const [col, ord, top] = CARAC[S.carac];
    const rot = { tipo: D.R.tipo, fase: D.R.fase, dow: DIA_C, cond: D.R.cond, tracado: D.R.tracado, pista: D.R.pista }[col];
    const lc = P.pctPorSexo(D, mc, (i) => { const v = D.oc[col][D.ev.oc[i]]; return v === 255 ? null : rot[v]; }, ord ? rot : null, top);
    if (lc.length) {
      const d2 = lc.map((x) => Math.abs(x.M - x.F)), im = d2.indexOf(Math.max(...d2));
      const tq = P.quiQuadrado(lc.map((x) => [x.nF, x.nM]));
      h += B.grafico("c4_carac", B.tabela([S.carac, "Feminino", "Masculino"], lc.map((x) => [x.cat, `${n(x.nF)} (${pct(x.F)})`, `${n(x.nM)} (${pct(x.M)})`])));
      figs.push(Object.assign({ id: "c4_carac" }, G.barrasSexo(lc, `A maior diferença está em “${lc[im].cat}”: ${pct(lc[im].F)} das condutoras vs. ${pct(lc[im].M)} dos condutores`,
        `% dos condutores de cada sexo por ${S.carac.toLowerCase()}` + (tq ? ` · V de Cramér = ${n(tq.v, 3)} (${tq.efeito})` : ""), "% dos condutores")));
    }
    const fz = P.pctPorSexo(D, mc, (i) => { const v = D.oc.fase[D.ev.oc[i]]; return v === 255 ? null : D.R.fase[v]; }, D.R.fase).find((x) => x.cat === "Plena Noite");
    h += B.leitura(`Entre os condutores, a letalidade é de <b>${pct(fem.letalidade, 2)}</b> para mulheres e <b>${pct(mas.letalidade, 2)}</b> para homens${rr ? `, um risco relativo de ${vezes(rr.rr, 2)}` : ""}. A associação entre sexo e estado físico, porém, tem efeito <b>${teste ? teste.efeito : "—"}</b> (V = ${teste ? n(teste.v, 3) : "—"}): o sexo explica pouco da gravidade.${fz ? ` Elas também dirigiam menos à noite (${pct(fz.F, 0)} contra ${pct(fz.M, 0)}), justamente o período mais letal do KM 2.` : ""}`);
    h += fem.letSup < mas.letInf
      ? B.descoberta("Os dados <b>não sustentam</b> a ideia de que acidentes com mulheres ao volante são mais graves: apontam o contrário. A diferença diminui quando controlamos veículo, idade e horário, mas não desaparece. Ainda assim, o efeito é pequeno: <b>o tipo de veículo e o horário pesam muito mais do que o sexo de quem dirige</b>.")
      : B.descoberta("Neste recorte, a letalidade das condutoras <b>não é claramente menor</b> que a dos condutores: os intervalos de confiança se sobrepõem ou a direção se inverte. Veja o KM 5 para o resultado na base completa.");
    return { html: h, figs };
  }

  // ======================= KM 5 =======================
  function km5(c) {
    const { D, pre } = c, H = pre.hip, v = H.veredito, te = H.teste_estado, tc = H.teste_causa, oa = H.or_ajustada;
    let semS = 0, semE = 0, fat = 0;
    for (let i = 0; i < D.nEv; i++) { if (D.ev.sexo[i] === 255) semS++; if (D.ev.estado[i] === 255) semE++; }
    for (let i = 0; i < D.nOc; i++) fat += D.oc.fatal[i];
    let h = B.marco(5, "Descobertas", "Afinal, o ditado se sustenta?",
      "Os veredictos abaixo usam a <b>base completa</b> (jan/2024 a ago/2026), independente dos filtros, e seguem regras fixas: uma hipótese só é confirmada ou rejeitada quando os intervalos de confiança não se sobrepõem.");
    h += B.kpis([
      { rot: "Mulheres entre os condutores", val: pct(H.share_f_condutores), sub: `de ${n(H.n_condutores)} condutores com sexo informado` },
      { rot: "Letalidade · condutoras", val: pct(H.let_f, 2), sub: `IC 95%: ${pct(H.let_f_ic[0], 2)} a ${pct(H.let_f_ic[1], 2)}` },
      { rot: "Letalidade · condutores", val: pct(H.let_m, 2), sub: `IC 95%: ${pct(H.let_m_ic[0], 2)} a ${pct(H.let_m_ic[1], 2)}` },
      { rot: "Chance de óbito H ÷ M, ajustada", val: vezes(oa.or, 2), sub: `sem ajuste: ${vezes(H.or_bruta.or, 2)}` }]);
    const exc = H.excecoes.length ? " (exceção: " + H.excecoes.map(([g, nf]) => `${g.toLowerCase()}, com só ${n(nf)} condutoras e IC amplo`).join(", ") + ")" : "";
    h += `<h3 class="sub">Hipóteses testadas</h3><div class="hips">` +
      B.hip("H1", "Mulheres se envolvem em mais acidentes", v.H1, `As mulheres são só ${pct(H.share_f_condutores)} dos condutores envolvidos. Isso <b>não</b> é taxa de risco: a base não informa quantas mulheres dirigem nem quantos km rodam. Sem esse denominador, não dá para dizer quem se acidenta mais <i>por km dirigido</i>.`,
        "Evidência: participação nos registros · falta o dado de exposição (habilitados, frota, km)") +
      B.hip("H2", "Acidentes com condutoras são mais graves", v.H2, v.H2 === "nao_confirmada"
        ? `É o contrário: a letalidade das condutoras (${pct(H.let_f, 2)}) é menor que a dos condutores (${pct(H.let_m, 2)}), e os intervalos de confiança não se sobrepõem. O índice de gravidade segue a mesma direção (${pct(H.grav_f)} vs. ${pct(H.grav_m)}).`
        : `Letalidade das condutoras: ${pct(H.let_f, 2)}; dos condutores: ${pct(H.let_m, 2)}.`,
        `Evidência: χ² = ${n(te.qui2)}, p < 0,001 · V de Cramér = ${n(te.v, 3)} (efeito ${te.efeito})`) +
      B.hip("H3", "O perfil de causas é diferente entre os sexos", v.H3, `Em acidentes com um único veículo, falhas de reação aparecem mais entre mulheres; álcool, velocidade e sono aparecem mais entre homens. A diferença é estatisticamente clara, mas de <b>efeito ${tc.efeito}</b>: os perfis se parecem mais do que diferem.`,
        `Evidência: χ² = ${n(tc.qui2)}, gl = ${tc.gl}, V de Cramér = ${n(tc.v, 3)} · n = ${n(tc.n)} condutores em acidentes de veículo único`) +
      B.hip("H4", "A diferença de letalidade persiste com controles", v.H4, `Em ${H.estratos_m_maior} de ${H.estratos_validos} tipos de veículo com dados suficientes, a letalidade dos homens é maior${exc}. Na regressão logística, a razão de chances cai de ${n(H.or_bruta.or, 2)} para ${n(oa.or, 2)}: parte da diferença vinha do veículo, da idade e do horário, mas não toda.`,
        `Evidência: OR ajustada = ${n(oa.or, 2)} (IC 95%: ${n(oa.ic_inf, 2)} a ${n(oa.ic_sup, 2)}) · ajustada por veículo, idade, fase do dia, trecho e dia`) + `</div>`;
    h += `<h3 class="sub">O que aprendemos</h3>` + B.leitura(`<ol>
      <li><b>O problema é estável.</b> Cerca de ${pct(100 * fat / D.nOc, 0)} das ocorrências têm morte, ano após ano (KM 1).</li>
      <li><b>Volume e letalidade apontam para lugares diferentes.</b> Os acidentes se concentram nos grandes corredores e no horário de pico, mas os que matam se concentram à noite e de madrugada (KM 2).</li>
      <li><b>Mulheres são minoria ao volante e maioria na carona.</b> São ${pct(H.share_f_condutores, 0)} dos condutores e ${pct(H.share_f_passageiros, 0)} dos passageiros, e dirigiam outros tipos de veículo (KM 3).</li>
      <li><b>Os dados não sustentam o ditado.</b> Quando dirigem, mulheres têm acidentes de menor letalidade, mesmo comparando o mesmo tipo de veículo, idade e horário (KM 4).</li>
      <li><b>O sexo pesa pouco.</b> Veículo (moto, bicicleta), madrugada, trecho rural e idade 60+ explicam muito mais da gravidade (KM 4).</li></ol>`, "Principais descobertas");
    h += `<div class="duas">` + B.leitura(`<ul>
      <li><b>Sem exposição:</b> não há km rodados nem número de condutores por sexo. Nenhum indicador aqui é risco por motorista.</li>
      <li><b>Só quem se acidentou:</b> a base condiciona ao acidente; comparações de gravidade valem <i>dado que houve acidente</i>.</li>
      <li><b>Causa é da ocorrência:</b> por isso a análise de causas prioriza acidentes de veículo único.</li>
      <li><b>Associação, não causa:</b> velocidade, cinto/capacete e estado do veículo não estão na base.</li>
      <li><b>Ausentes:</b> ${pct(100 * semS / D.nEv)} dos envolvidos sem sexo e ${pct(100 * semE / D.nEv)} sem estado físico ficam fora dos percentuais.</li>
      <li><b>2026 parcial:</b> só até agosto; comparar pela mesma janela de meses.</li></ul>`, "Limitações") +
      B.leitura(`<ul>
      <li><b>Normalizar por exposição:</b> cruzar com habilitados por sexo e UF (Senatran) para estimar taxa por condutor.</li>
      <li><b>Todas as causas:</b> usar a base <code>todas_causas_tipos</code>, que hoje entra só como contagem, para analisar combinações de causas.</li>
      <li><b>Modelos por veículo:</b> ajustar modelos separados para motos e automóveis, onde há mais mulheres.</li>
      <li><b>Série histórica:</b> incluir anos anteriores a 2024 para testar tendência.</li>
      <li><b>Interação:</b> testar se o efeito do sexo muda com a idade (jovens vs. 60+).</li></ul>`, "Próximas investigações") + `</div>`;
    h += `<details class="cartao"><summary>Registro de qualidade dos dados (ETL + painel)</summary>${B.tabela(["Base", "Verificação", "Registros", "Tratamento"],
      pre.qualidade.map((q) => [q.base, q["verificação"], n(q.registros_afetados), q.tratamento]))}</details>`;
    h += `<details class="cartao"><summary>Dicionário de indicadores</summary>${B.tabela(["Indicador", "Definição", "Fórmula", "Tabela"],
      pre.kpis.map((k) => [k.indicador, k["definição"], k["fórmula"], k.tabela]))}</details>`;
    h += B.descoberta("<b>Resposta à pergunta do título:</b> nos acidentes das rodovias federais, ter uma mulher ao volante está associado a <b>menor</b> letalidade, não maior. O que a base não responde é se as mulheres se acidentam mais ou menos <i>por km dirigido</i>, porque falta o dado de exposição. A crença popular não encontra apoio nos dados disponíveis.");
    return { html: h, figs: [] };
  }

  const API = { capitulos: [km1, km2, km3, km4, km5], n, pct, MESES };
  if (typeof module !== "undefined" && module.exports) module.exports = API; else raiz.CAP = API;
})(typeof window !== "undefined" ? window : globalThis);
