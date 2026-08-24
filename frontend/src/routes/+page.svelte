<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { base } from '$app/paths';

  let summary = $state(null);
  let loading = $state(true);
  let error = $state('');
  let selectedCategory = $state('all');
  let lang = $state('el');
  let currentDate = $state('');

  const categoryLabels = {
    politics: { el: 'Πολιτική', en: 'Politics' },
    economy: { el: 'Οικονομία', en: 'Economy' },
    society: { el: 'Κοινωνία', en: 'Society' },
    world: { el: 'Κόσμος', en: 'World' },
    culture: { el: 'Πολιτισμός', en: 'Culture' },
    opinion: { el: 'Απόψεις', en: 'Opinion' },
    sports: { el: 'Αθλητικά', en: 'Sports' },
    social: { el: 'Social Media', en: 'Social Media' },
    ai: { el: 'Τεχνητή Νοημοσύνη', en: 'AI' },
  };

  onMount(async () => {
    const savedLang = localStorage?.getItem?.('lang');
    if (savedLang) lang = savedLang;
    window.addEventListener('langchange', (e) => { lang = e.detail; });

    // Get date from URL or load latest
    const urlDate = $page.url.searchParams.get('date');
    const urlCat = $page.url.searchParams.get('category');
    if (urlCat) selectedCategory = urlCat;

    try {
      // Load index to get available dates
      const indexRes = await fetch(`${base}/data/index.json`);
      if (!indexRes.ok) throw new Error('No data available yet');
      const index = await indexRes.json();

      currentDate = urlDate || index.dates[0];
      if (!currentDate) throw new Error('No dates available');

      // Load summary for the date
      const summaryRes = await fetch(`${base}/data/${currentDate}/summary.json`);
      if (!summaryRes.ok) throw new Error(`No data for ${currentDate}`);
      const s = await summaryRes.json();

      // Some pipeline runs store top_items as id strings instead of embedded
      // article objects. Resolve ids by fetching the per-category files.
      const cats = Object.entries(s.categories || {});
      const needsResolve = cats.filter(([, c]) =>
        Array.isArray(c.top_items) && c.top_items.some((t) => typeof t === 'string'));
      if (needsResolve.length > 0) {
        await Promise.all(needsResolve.map(async ([cat, c]) => {
          try {
            const res = await fetch(`${base}/data/${currentDate}/${cat}.json`);
            if (!res.ok) throw new Error();
            const catData = await res.json();
            const byId = Object.fromEntries((catData.items || []).map((it) => [it.id, it]));
            c.top_items = c.top_items
              .map((t) => (typeof t === 'string' ? byId[t] : t))
              .filter(Boolean);
          } catch {
            c.top_items = c.top_items.filter((t) => typeof t !== 'string');
          }
        }));
      }
      summary = s;
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  function getCategoryLabel(cat) {
    return categoryLabels[cat]?.[lang] || cat;
  }

  function catColor(cat) {
    return `var(--cat-${cat}, var(--color-accent))`;
  }

  function impColor(imp) {
    return imp >= 80 ? 'var(--imp-high)' : imp >= 60 ? 'var(--imp-mid)' : 'var(--imp-low)';
  }

  // The single most important article of the day (front-page lead)
  let hero = $derived.by(() => {
    if (!summary) return null;
    let best = null;
    for (const [cat, c] of Object.entries(summary.categories || {})) {
      if (cat === 'ai') continue; // ai items are cross-listed duplicates
      for (const it of c.top_items || []) {
        if (typeof it === 'object' && (!best || (it.importance || 0) > (best.importance || 0))) {
          best = it;
        }
      }
    }
    return best;
  });

  function sectionItems(cat, catData) {
    const items = (catData.top_items || []).filter((t) => typeof t === 'object');
    // On the "all" front page the hero already appears at the top
    if (selectedCategory === 'all' && hero && cat === hero.category) {
      return items.filter((it) => it.id !== hero.id);
    }
    return items;
  }
</script>

<svelte:head>
  <title>{lang === 'el' ? 'Ελληνικά Νέα - AI Digest' : 'Greek News - AI Digest'}</title>
</svelte:head>

{#if loading}
  <div class="flex justify-center items-center py-20">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-accent)]"></div>
  </div>
{:else if error}
  <div class="text-center py-20">
    <h2 class="font-serif-news text-2xl font-bold mb-4">
      {lang === 'el' ? 'Δεν υπάρχουν δεδομένα ακόμα' : 'No data available yet'}
    </h2>
    <p class="text-[var(--color-text-secondary)]">
      {lang === 'el'
        ? 'Η pipeline δεν έχει τρέξει ακόμα. Εκτελέστε: python run_pipeline.py'
        : 'The pipeline hasn\'t run yet. Run: python run_pipeline.py'}
    </p>
  </div>
{:else if summary}
  <!-- Dateline -->
  <div class="fade-up text-center mb-6">
    <p class="font-serif-news text-sm text-[var(--color-text-secondary)]">
      {new Date(currentDate + 'T00:00:00').toLocaleDateString(lang === 'el' ? 'el-GR' : 'en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
      })}
      &nbsp;&middot;&nbsp;
      {summary.article_count || 0} {lang === 'el' ? 'άρθρα' : 'articles'}
    </p>
  </div>

  <!-- Front page: hero + executive summary -->
  <div class="fade-up rule-double pt-5 mb-10 grid gap-8 lg:grid-cols-[1.6fr_1fr]" style="animation-delay: 0.05s">
    <div>
      {#if hero && selectedCategory === 'all'}
        <p class="kicker" style="color: {catColor(hero.category)}">
          {lang === 'el' ? 'Κυριο θεμα' : 'Lead story'} &middot; {getCategoryLabel(hero.category)}
        </p>
        <a href={hero.url} target="_blank" rel="noopener noreferrer"
           class="font-serif-news block text-3xl sm:text-4xl font-semibold leading-tight mt-2 hover:text-[var(--color-accent)] transition-colors">
          {hero.title}
        </a>
        <p class="font-serif-news text-base leading-relaxed mt-3 text-[var(--color-text)]">
          {hero.summary?.[lang] || hero.summary?.el || ''}
        </p>
        <p class="text-xs text-[var(--color-text-secondary)] mt-3">
          {hero.author || hero.source}
          &nbsp;&middot;&nbsp;
          <span style="color: {impColor(hero.importance)}">{lang === 'el' ? 'Σημαντικότητα' : 'Importance'} {hero.importance}</span>
        </p>
      {/if}

      <!-- Top topics under the hero -->
      {#if summary.top_topics?.length > 0}
        <div class="rule-thin mt-6 pt-4">
          <p class="kicker text-[var(--color-text-secondary)] mb-3">
            {lang === 'el' ? 'Κορυφαια θεματα' : 'Top topics'}
          </p>
          <div class="grid gap-x-6 gap-y-3 sm:grid-cols-2">
            {#each summary.top_topics as topic, i}
              <div class="flex gap-3">
                <span class="font-serif-news text-2xl font-semibold leading-none"
                      style="color: {impColor(topic.importance)}">{i + 1}</span>
                <div>
                  <p class="font-serif-news font-semibold text-sm leading-snug">
                    {topic.name?.[lang] || topic.name?.el || ''}
                  </p>
                  <p class="text-xs text-[var(--color-text-secondary)] leading-relaxed mt-0.5">
                    {topic.description?.[lang] || topic.description?.el || ''}
                  </p>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <!-- Executive summary sidebar -->
    {#if summary.executive_summary}
      <aside class="lg:border-l lg:border-[var(--color-rule)] lg:pl-8">
        <p class="kicker text-[var(--color-text-secondary)]">
          {lang === 'el' ? 'Η συνοψη της ημερας' : 'The day in brief'}
        </p>
        <div class="font-serif-news italic text-sm leading-relaxed whitespace-pre-line mt-2 text-[var(--color-text)]">
          {summary.executive_summary[lang] || summary.executive_summary.el || summary.executive_summary.en || ''}
        </div>
      </aside>
    {/if}
  </div>

  <!-- Category Filter -->
  <div class="fade-up flex flex-wrap gap-x-5 gap-y-2 mb-8 rule-double pt-3" style="animation-delay: 0.1s">
    <button
      class="kicker pb-1 border-b-2 transition-colors {selectedCategory === 'all' ? 'border-[var(--color-ink)] text-[var(--color-text)]' : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text)]'}"
      onclick={() => selectedCategory = 'all'}>
      {lang === 'el' ? 'Όλα' : 'All'}
    </button>
    {#each Object.keys(summary.categories || {}) as cat}
      <button
        class="kicker pb-1 border-b-2 transition-colors {selectedCategory === cat ? 'text-[var(--color-text)]' : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text)]'}"
        style={selectedCategory === cat ? `border-color: ${catColor(cat)}` : ''}
        onclick={() => selectedCategory = cat}>
        {getCategoryLabel(cat)}
        <span class="opacity-60 normal-case tracking-normal">({summary.categories[cat].item_count})</span>
      </button>
    {/each}
  </div>

  <!-- News sections -->
  <section>
    {#each Object.entries(summary.categories || {}) as [cat, catData], ci}
      {#if selectedCategory === 'all' || selectedCategory === cat}
        <div class="fade-up mb-10" style="animation-delay: {0.12 + ci * 0.04}s">
          <div class="flex items-baseline gap-3 border-b-2 pb-1 mb-4" style="border-color: {catColor(cat)}">
            <h2 class="kicker" style="color: {catColor(cat)}">
              {getCategoryLabel(cat)}
            </h2>
            {#if catData.item_count > (catData.top_items?.length || 0)}
              <span class="text-xs text-[var(--color-text-secondary)]">
                {lang === 'el' ? `${catData.top_items?.length || 0} από ${catData.item_count}` : `${catData.top_items?.length || 0} of ${catData.item_count}`}
              </span>
            {/if}
          </div>
          <div>
            {#each sectionItems(cat, catData) as item, ii}
              <article class="hover-lift rounded-md px-3 py-3 -mx-3 {ii > 0 ? 'rule-thin' : ''}">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1 min-w-0">
                    <a href={item.url} target="_blank" rel="noopener noreferrer"
                       class="font-serif-news font-semibold text-lg leading-snug hover:text-[var(--color-accent)] transition-colors">
                      {item.title}
                    </a>
                    <p class="text-sm text-[var(--color-text-secondary)] leading-relaxed mt-1">
                      {item.summary?.[lang] || item.summary?.el || item.summary?.en || ''}
                    </p>
                    <div class="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs text-[var(--color-text-secondary)]">
                      {#if item.sentiment === 'positive'}
                        <span class="inline-flex items-center gap-1" style="color: var(--sent-pos)">
                          <span class="inline-block w-1.5 h-1.5 rounded-full" style="background: var(--sent-pos)"></span>
                          {lang === 'el' ? 'θετικό' : 'positive'}
                        </span>
                      {:else if item.sentiment === 'negative'}
                        <span class="inline-flex items-center gap-1" style="color: var(--sent-neg)">
                          <span class="inline-block w-1.5 h-1.5 rounded-full" style="background: var(--sent-neg)"></span>
                          {lang === 'el' ? 'αρνητικό' : 'negative'}
                        </span>
                      {/if}
                      {#if item.author && item.author !== 'Καθημερινή'}
                        <span>{item.author}</span>
                      {/if}
                      {#if item.published}
                        <span>{new Date(item.published).toLocaleTimeString(lang === 'el' ? 'el-GR' : 'en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                      {/if}
                      {#each (item.tags?.[lang] || item.tags?.el || []).slice(0, 3) as tag}
                        <span class="px-1.5 py-0.5 rounded border border-[var(--color-border)]">{tag}</span>
                      {/each}
                    </div>
                  </div>
                  <div class="flex-shrink-0 text-right w-10">
                    <span class="font-serif-news text-lg font-semibold" style="color: {impColor(item.importance)}">
                      {item.importance}
                    </span>
                    <div class="h-0.5 rounded-full mt-1 bg-[var(--color-border)]">
                      <div class="h-0.5 rounded-full" style="width: {item.importance}%; background: {impColor(item.importance)}"></div>
                    </div>
                  </div>
                </div>
              </article>
            {/each}
          </div>
        </div>
      {/if}
    {/each}
  </section>

  <!-- Source note -->
  {#if summary.source_note}
    <p class="rule-thin pt-4 mt-2 text-xs text-[var(--color-text-secondary)]">
      {summary.source_note}
    </p>
  {/if}
{/if}
