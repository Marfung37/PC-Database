<script lang="ts">
  import FumenRender from '$lib/components/FumenRender.svelte';

  let { fumen, solve_percent } = $props();
</script>

<div class="card flex flex-col">
  <div class="flex min-w-80 basis-1/2 items-center justify-center p-4 md:basis-1/3 xl:basis-1/4">
    <FumenRender {fumen} minHeight={4} />
  </div>
  <div class="flex justify-center">
    <p>{solve_percent}%</p>
  </div>
</div>
