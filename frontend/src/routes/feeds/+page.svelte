<script>
  let lang = $state('el');
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  onMount(() => {
    const saved = localStorage?.getItem?.('lang');
    if (saved) lang = saved;
  });

  const feeds = [
    { name: { el: 'Κύριο Feed', en: 'Main Feed' }, url: `${base}/data/feeds/main.xml`, desc: { el: 'Ημερήσια σύνοψη + κορυφαία', en: 'Daily summary + top stories' }},
    { name: { el: 'Πολιτική', en: 'Politics' }, url: `${base}/data/feeds/politics.xml`, desc: { el: 'Πολιτικά νέα', en: 'Political news' }},
    { name: { el: 'Οικονομία', en: 'Economy' }, url: `${base}/data/feeds/economy.xml`, desc: { el: 'Οικονομικά νέα', en: 'Economic news' }},
    { name: { el: 'Κοινωνία', en: 'Society' }, url: `${base}/data/feeds/society.xml`, desc: { el: 'Κοινωνικά νέα', en: 'Social news' }},
    { name: { el: 'Κόσμος', en: 'World' }, url: `${base}/data/feeds/world.xml`, desc: { el: 'Διεθνή νέα', en: 'International news' }},
    { name: { el: 'Πολιτισμός', en: 'Culture' }, url: `${base}/data/feeds/culture.xml`, desc: { el: 'Πολιτιστικά νέα', en: 'Cultural news' }},
  ];
</script>

<svelte:head>
  <title>RSS Feeds - Greek News AI Digest</title>
</svelte:head>

<h1 class="text-3xl font-bold mb-6">RSS Feeds</h1>

<p class="text-[var(--color-text-secondary)] mb-8">
  {lang === 'el'
    ? 'Εγγραφείτε στα Atom RSS feeds για να λαμβάνετε ενημερώσεις στον RSS reader σας.'
    : 'Subscribe to Atom RSS feeds to get updates in your RSS reader.'}
</p>

<div class="space-y-3">
  {#each feeds as feed}
    <div class="flex items-center justify-between p-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
      <div>
        <h3 class="font-medium">{feed.name[lang]}</h3>
        <p class="text-sm text-[var(--color-text-secondary)]">{feed.desc[lang]}</p>
      </div>
      <a href={feed.url}
         class="px-4 py-2 rounded-lg bg-primary-600 text-white text-sm hover:bg-primary-700 transition flex-shrink-0">
        {lang === 'el' ? 'Εγγραφή' : 'Subscribe'}
      </a>
    </div>
  {/each}
</div>
