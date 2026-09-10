<script lang="ts">
  import { page } from '$app/state';
  import { resolve } from '$app/paths';
  import { enhance } from '$app/forms';
  import { goto, invalidate } from '$app/navigation';
  import { m } from '$lib/paraglide/messages.js';
  import SetupMiniInfo from '$lib/components/SetupMiniInfo.svelte';

  const { data, form } = $props();

  let setups = $derived(data.setups ?? []);
  const uniqueLeftovers = $derived(data.leftovers ?? []);
  let hasMore = $derived(data.hasMore ?? false);

  const setupGroups = $derived([...Map.groupBy(setups, (setup) => setup.leftover)]);

  const pcs = [
    { id: 1, pc: '1st' },
    { id: 2, pc: '2nd' },
    { id: 3, pc: '3rd' },
    { id: 4, pc: '4th' },
    { id: 5, pc: '5th' },
    { id: 6, pc: '6th' },
    { id: 7, pc: '7th' },
    { id: 8, pc: '8th' },
    { id: 9, pc: '9th' }
  ];

  let params = $derived(page.url.searchParams);
  const pcNumber: number | null = $derived(
    params.get('pc') !== null ? parseInt(params.get('pc')!) : null
  );
  const leftover = $derived(params.get('leftover'));

  async function changePC(value: number) {
    if (value == -1) {
      params.delete('pc');
    } else {
      params.set('pc', String(value));
    }
    params.set('page', String(1));

    await goto(resolve(`/database?${params.toString()}`));
    await invalidate('setups');
  }

  async function changeLeftover(value: string) {
    params.set('leftover', value);
    params.set('page', String(1));

    await goto(resolve(`/database?${params.toString()}`));
    await invalidate('setups');
  }
</script>

<div class="hero min-h-[20vh]">
  <div class="hero-content py-12 text-center">
    <div class="container flex flex-col gap-2">
      <div
        class="from-primary to-accent mb-3 bg-linear-to-r bg-clip-text pb-1 text-xl font-bold text-transparent md:mb-7 md:text-3xl"
      >
        {m.nav_database()}
      </div>
    </div>
  </div>
</div>

<div class="flex flex-col items-center">
  <section id="filter">
    <label for="pc">{m.database_pc_number()}</label>
    <select
      id="pc"
      class="bg-base-300 rounded"
      onchange={(e) => changePC(Number(e.currentTarget.value))}
    >
      <option value={-1}>All</option>
      {#each pcs as pc (pc.id)}
        <option value={pc.id} selected={pc.id == pcNumber}>{pc.pc}</option>
      {/each}
    </select>

    {#if pcNumber !== null}
      <label for="leftover">{m.database_leftover()}</label>
      <select
        id="leftover"
        class="bg-base-300 rounded"
        onchange={(e) => changeLeftover(e.currentTarget.value)}
      >
        <option value={-1}>All</option>
        {#each uniqueLeftovers as lo (lo)}
          <option value={lo} selected={lo == leftover}>{lo}</option>
        {/each}
      </select>
    {/if}
  </section>
  <div id="results" class="flex flex-col m-4">
    {#each setupGroups as [leftover, setups] (leftover)}
      <div>
        <h3 class="mino text-4xl pl-8">{leftover}</h3>
        <div class="flex flex-wrap">
          {#each setups as setup (setup.setup_id)}
            <div class="basis-1/4 p-8">
              <SetupMiniInfo fumen={setup.fumen} solve_percent={setup.solve_percent} />
            </div>
          {/each}
        </div>
      </div>
    {/each}
    {#if hasMore && setups.length > 0}
      <form
        method="POST"
        action="?/loadMore"
        use:enhance={() => {
          return async ({ result }) => {
            if (result.type === 'success') {
              const data = result.data as {
                setups: typeof setups;
                hasMore: boolean;
              };
              setups = [...setups, ...data.setups];
              hasMore = data.hasMore;
            } else if (result.type === 'failure') {
              console.error(result.data);
            }
          };
        }}
        class="w-full flex justify-center"
      >
        <input name="pc" value={pcNumber} type="hidden" />
        <input name="leftover" value={leftover} type="hidden" />
        <input name="cursor" value={setups[setups.length - 1].setup_id} type="hidden" />
        <button type="submit" class="btn p-6 bg-info text-info-content hover:bg-info/70 text-lg"
          >Load More...</button
        >
      </form>
    {/if}
  </div>
</div>
