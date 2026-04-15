<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

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
  };

  onMount(async () => {
    const savedLang = localStorage?.getItem?.('lang');
    if (savedLang) lang = savedLang;

    // Get date from URL or load latest
    const urlDate = $page.url.searchParams.get('date');
    const urlCat = $page.url.searchParams.get('category');
    if (urlCat) selectedCategory = urlCat;

    try {
      // Load index to get available dates
      const indexRes = await fetch('/data/index.json');
      if (!indexRes.ok) throw new Error('No data available yet');
      const index = await indexRes.json();

      currentDate = urlDate || index.dates[0];
      if (!currentDate) throw new Error('No dates available');

      // Load summary for the date
      const summaryRes = await fetch(`/data/${currentDate}/summary.json`);
      if (!summaryRes.ok) throw new Error(`No data for ${currentDate}`);
      summary = await summaryRes.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  function getCategoryLabel(cat) {
    return categoryLabels[cat]?.[lang] || cat;
  }

  $effect(() => {
    const savedLang = localStorage?.getItem?.('lang');
    if (savedLang && savedLang !== lang) lang = savedLang;
  });
</script>

<svelte:head>
  <title>{lang === 'el' ? 'Ελληνικά Νέα - AI Digest' : 'Greek News - AI Digest'}</title>
</svelte:head>

{#if loading}
  <div class="flex justify-center items-center py-20">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
  </div>
{:else if error}
  <div class="text-center py-20">
    <h2 class="text-2xl font-bold mb-4">
      {lang === 'el' ? 'Δεν υπάρχουν δεδομένα ακόμα' : 'No data available yet'}
    </h2>
    <p class="text-[var(--color-text-secondary)]">
      {lang === 'el'
        ? 'Η pipeline δεν έχει τρέξει ακόμα. Εκτελέστε: python run_pipeline.py'
        : 'The pipeline hasn\'t run yet. Run: python run_pipeline.py'}
    </p>
  </div>
{:else if summary}
  <!-- Date header -->
  <div class="mb-8">
    <h1 class="text-3xl font-bold">
      {lang === 'el' ? 'Ημερήσια Ανασκόπηση' : 'Daily Digest'}
    </h1>
    <p class="text-[var(--color-text-secondary)] mt-1">
      {new Date(currentDate + 'T00:00:00').toLocaleDateString(lang === 'el' ? 'el-GR' : 'en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
      })}
    </p>
  </div>

  <!-- Executive Summary -->
  {#if summary.executive_summary}
    <section class="mb-10 bg-[var(--color-bg-secondary)] rounded-xl p-6 border border-[var(--color-border)]">
      <h2 class="text-xl font-semibold mb-4">
        {lang === 'el' ? 'Σύνοψη' : 'Executive Summary'}
      </h2>
      <div class="prose-greek whitespace-pre-line leading-relaxed">
        {summary.executive_summary[lang] || summary.executive_summary.el || summary.executive_summary.en || ''}
      </div>
    </section>
  {/if}

  <!-- Top Topics -->
  {#if summary.top_topics?.length > 0}
    <section class="mb-10">
      <h2 class="text-xl font-semibold mb-4">
        {lang === 'el' ? 'Κορυφαία Θέματα' : 'Top Topics'}
      </h2>
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {#each summary.top_topics as topic}
          <div class="p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
            <h3 class="font-semibold text-primary-600 dark:text-primary-400">
              {topic.name?.[lang] || topic.name?.el || ''}
            </h3>
            <p class="text-sm mt-2 text-[var(--color-text-secondary)]">
              {topic.description?.[lang] || topic.description?.el || ''}
            </p>
            <span class="inline-block mt-2 text-xs px-2 py-0.5 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300">
              {lang === 'el' ? 'Σημαντικότητα' : 'Importance'}: {topic.importance}
            </span>
          </div>
        {/each}
      </div>
    </section>
  {/if}

  <!-- Category Filter -->
  <div class="flex flex-wrap gap-2 mb-6">
    <button
      class="px-3 py-1.5 rounded-full text-sm transition {selectedCategory === 'all' ? 'bg-primary-600 text-white' : 'bg-[var(--color-bg-secondary)] border border-[var(--color-border)] hover:border-primary-400'}"
      onclick={() => selectedCategory = 'all'}>
      {lang === 'el' ? 'Όλα' : 'All'}
    </button>
    {#each Object.keys(summary.categories || {}) as cat}
      <button
        class="px-3 py-1.5 rounded-full text-sm transition {selectedCategory === cat ? 'bg-primary-600 text-white' : 'bg-[var(--color-bg-secondary)] border border-[var(--color-border)] hover:border-primary-400'}"
        onclick={() => selectedCategory = cat}>
        {getCategoryLabel(cat)}
        <span class="ml-1 opacity-60">({summary.categories[cat].item_count})</span>
      </button>
    {/each}
  </div>

  <!-- News Items -->
  <section>
    {#each Object.entries(summary.categories || {}) as [cat, catData]}
      {#if selectedCategory === 'all' || selectedCategory === cat}
        <div class="mb-8">
          <h2 class="text-lg font-semibold mb-3 text-primary-700 dark:text-primary-400">
            {getCategoryLabel(cat)}
          </h2>
          <div class="space-y-3">
            {#each catData.top_items || [] as item}
              <article class="p-4 rounded-lg border border-[var(--color-border)] hover:border-primary-400 transition bg-[var(--color-bg)]">
                <div class="flex items-start justify-between gap-3">
                  <div class="flex-1">
                    <a href={item.url} target="_blank" rel="noopener noreferrer"
                       class="font-medium hover:text-primary-600 transition">
                      {item.title}
                    </a>
                    <p class="text-sm text-[var(--color-text-secondary)] mt-1">
                      {item.summary?.[lang] || item.summary?.el || item.summary?.en || ''}
                    </p>
                    <div class="flex items-center gap-3 mt-2 text-xs text-[var(--color-text-secondary)]">
                      <span>{item.source}</span>
                      {#if item.published}
                        <span>{new Date(item.published).toLocaleTimeString(lang === 'el' ? 'el-GR' : 'en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                      {/if}
                      {#each (item.tags?.[lang] || item.tags?.el || []).slice(0, 3) as tag}
                        <span class="px-1.5 py-0.5 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)]">{tag}</span>
                      {/each}
                    </div>
                  </div>
                  <div class="flex-shrink-0">
                    <span class="inline-block px-2 py-0.5 rounded text-xs font-medium
                      {item.importance >= 80 ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                       item.importance >= 60 ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                       'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}">
                      {item.importance}
                    </span>
                  </div>
                </div>
              </article>
            {/each}
          </div>
        </div>
      {/if}
    {/each}
  </section>

  <!-- Stats -->
  {#if summary.stats}
    <div class="mt-8 pt-6 border-t border-[var(--color-border)] text-sm text-[var(--color-text-secondary)]">
      {lang === 'el' ? 'Συλλέχθηκαν' : 'Collected'}: {summary.stats.total || 0} {lang === 'el' ? 'άρθρα' : 'articles'}
      &middot;
      {lang === 'el' ? 'Κόστος' : 'Cost'}: ${summary.cost?.total_usd?.toFixed(4) || '0.00'}
    </div>
  {/if}
{/if}
