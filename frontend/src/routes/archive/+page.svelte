<script>
  import { onMount } from 'svelte';

  let dates = $state([]);
  let loading = $state(true);
  let lang = $state('el');

  onMount(async () => {
    const savedLang = localStorage?.getItem?.('lang');
    if (savedLang) lang = savedLang;

    try {
      const res = await fetch('/data/index.json');
      if (res.ok) {
        const data = await res.json();
        dates = data.dates || [];
      }
    } catch {}
    loading = false;
  });
</script>

<svelte:head>
  <title>{lang === 'el' ? 'Αρχείο' : 'Archive'} - Greek News AI Digest</title>
</svelte:head>

<h1 class="text-3xl font-bold mb-6">
  {lang === 'el' ? 'Αρχείο' : 'Archive'}
</h1>

{#if loading}
  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
{:else if dates.length === 0}
  <p class="text-[var(--color-text-secondary)]">
    {lang === 'el' ? 'Δεν υπάρχουν δεδομένα ακόμα.' : 'No data available yet.'}
  </p>
{:else}
  <div class="grid gap-3 md:grid-cols-3 lg:grid-cols-4">
    {#each dates as date}
      <a href="/?date={date}"
         class="block p-4 rounded-lg border border-[var(--color-border)] hover:border-primary-400 bg-[var(--color-bg-secondary)] transition">
        <div class="font-medium">
          {new Date(date + 'T00:00:00').toLocaleDateString(lang === 'el' ? 'el-GR' : 'en-US', {
            weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
          })}
        </div>
      </a>
    {/each}
  </div>
{/if}
