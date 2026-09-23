<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount } from 'svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';
	import Spinner from '$lib/components/common/Spinner.svelte';

	let prompt = $state('');
	let negativePrompt = $state('');
	let selectedEngine = $state('openai');
	let selectedModel = $state('');
	let selectedSize = $state('512x512');
	let steps = $state(30);

	let models = $state<{ id: string; name: string }[]>([]);
	let loadingModels = $state(false);

	let generating = $state(false);
	let generatedImages = $state<{ url: string; prompt: string }[]>([]);

	const engines = [
		{ id: 'openai', name: 'OpenAI' },
		{ id: 'huggingface', name: 'Hugging Face Free' },
		{ id: 'automatic1111', name: 'AUTOMATIC1111' },
		{ id: 'comfyui', name: 'ComfyUI' },
		{ id: 'ollama', name: 'Ollama' }
	];

	const sizes = ['512x512', '768x768', '1024x1024'];

	$effect(() => {
		if (selectedEngine) {
			fetchModels();
		}
	});

	async function fetchModels() {
		loadingModels = true;
		try {
			// In reality, this hits the API. If backend endpoint isn't fully ready, it will catch.
			const res = await fetch(`${WEBUI_API_BASE_URL}/image-studio/models?engine=${selectedEngine}`, {
				headers: {
					Authorization: `Bearer ${localStorage.token}`
				}
			});

			if (!res.ok) {
				throw new Error('Failed to fetch models');
			}
			const data = await res.json();
			models = data.models || [];
			if (models.length > 0 && !models.find((m) => m.id === selectedModel)) {
				selectedModel = models[0].id;
			}
		} catch (error) {
			console.error(error);
			models = [{ id: 'default', name: 'Default Model' }];
			selectedModel = 'default';
			// Suppress toast since backend might not exist yet
		} finally {
			loadingModels = false;
		}
	}

	async function generateImage() {
		if (!prompt) {
			toast.error('Please enter a prompt.');
			return;
		}
		
		generating = true;
		try {
			const res = await fetch(`${WEBUI_API_BASE_URL}/image-studio/generate`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${localStorage.token}`
				},
				body: JSON.stringify({
					prompt,
					negative_prompt: negativePrompt,
					engine: selectedEngine,
					model: selectedModel,
					size: selectedSize,
					steps
				})
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail || 'Generation failed');
			}

			const data = await res.json();
			
			if (data.images && data.images.length > 0) {
				for (const imgUrl of data.images) {
					generatedImages = [{ url: imgUrl, prompt }, ...generatedImages];
				}
				toast.success('Image generated successfully!');
			}
		} catch (error: any) {
			toast.error(error.message || 'An error occurred during generation.');
		} finally {
			generating = false;
		}
	}
	
	function downloadImage(url: string, promptText: string) {
		const a = document.createElement('a');
		a.href = url;
		a.download = `generated-${promptText.substring(0, 20).replace(/[^a-z0-9]/gi, '_')}.png`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
	}
</script>

<div class="h-full flex flex-col md:flex-row bg-zinc-900 text-zinc-100 overflow-hidden">
	<!-- Sidebar Settings -->
	<div class="w-full md:w-80 p-4 border-b md:border-b-0 md:border-r border-zinc-800 flex flex-col gap-6 overflow-y-auto bg-zinc-950/50">
		<div>
			<h2 class="text-xl font-semibold mb-1 text-zinc-100">Image Studio</h2>
			<p class="text-sm text-zinc-400">Generate AI images</p>
		</div>

		<div class="space-y-4">
			<div class="flex flex-col gap-1.5">
				<label for="engine" class="text-sm font-medium text-zinc-300">Engine</label>
				<select id="engine" bind:value={selectedEngine} class="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-sm text-zinc-100 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors">
					{#each engines as engine}
						<option value={engine.id}>{engine.name}</option>
					{/each}
				</select>
			</div>

			<div class="flex flex-col gap-1.5">
				<label for="model" class="text-sm font-medium text-zinc-300">Model</label>
				<div class="relative">
					<select id="model" bind:value={selectedModel} disabled={loadingModels} class="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-sm text-zinc-100 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors disabled:opacity-50">
						{#if loadingModels}
							<option value="">Loading...</option>
						{:else if models.length === 0}
							<option value="">No models found</option>
						{:else}
							{#each models as model}
								<option value={model.id}>{model.name}</option>
							{/each}
						{/if}
					</select>
				</div>
			</div>

			<div class="flex flex-col gap-1.5">
				<label for="size" class="text-sm font-medium text-zinc-300">Size</label>
				<select id="size" bind:value={selectedSize} class="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-sm text-zinc-100 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors">
					{#each sizes as size}
						<option value={size}>{size}</option>
					{/each}
				</select>
			</div>

			<div class="flex flex-col gap-1.5">
				<div class="flex justify-between">
					<label for="steps" class="text-sm font-medium text-zinc-300">Steps</label>
					<span class="text-sm text-zinc-400">{steps}</span>
				</div>
				<input id="steps" type="range" bind:value={steps} min="10" max="50" step="1" class="w-full accent-indigo-500" />
			</div>
		</div>
	</div>

	<!-- Main Content Area -->
	<div class="flex-1 flex flex-col h-full bg-zinc-900">
		<!-- Prompt Area -->
		<div class="p-6 border-b border-zinc-800 bg-zinc-900 shadow-sm">
			<div class="flex flex-col gap-4 max-w-4xl mx-auto">
				<div class="flex flex-col gap-1.5">
					<label for="prompt" class="text-sm font-medium text-zinc-300">Prompt</label>
					<textarea id="prompt" bind:value={prompt} placeholder="A futuristic city at sunset..." rows="3" class="w-full bg-zinc-800 border border-zinc-700 rounded-xl p-3 text-sm text-zinc-100 placeholder-zinc-500 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors resize-none"></textarea>
				</div>
				
				<div class="flex flex-col gap-1.5">
					<label for="neg_prompt" class="text-sm font-medium text-zinc-300">Negative Prompt <span class="text-zinc-500 font-normal">(Optional)</span></label>
					<input id="neg_prompt" type="text" bind:value={negativePrompt} placeholder="blurry, bad quality..." class="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors" />
				</div>
				
				<div class="flex justify-end pt-2">
					<button onclick={generateImage} disabled={generating || !prompt} class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
						{#if generating}
							<Spinner className="size-4" />
							<span>Generating...</span>
						{:else}
							<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
							<span>Generate</span>
						{/if}
					</button>
				</div>
			</div>
		</div>

		<!-- Gallery Area -->
		<div class="flex-1 p-6 overflow-y-auto">
			<div class="max-w-4xl mx-auto">
				{#if generatedImages.length === 0}
					<div class="h-64 flex flex-col items-center justify-center text-zinc-500 gap-4">
						<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
						<p>Your generated images will appear here</p>
					</div>
				{:else}
					<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
						{#each generatedImages as image (image.url)}
							<div class="bg-zinc-800 rounded-xl overflow-hidden border border-zinc-700 shadow-sm group hover:border-zinc-600 transition-colors">
								<div class="aspect-square relative overflow-hidden bg-zinc-900">
									<img src={image.url} alt={image.prompt} class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
									
									<div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
										<button onclick={() => downloadImage(image.url, image.prompt)} class="bg-white/10 hover:bg-white/20 text-white rounded-full p-3 backdrop-blur-sm transition-colors" title="Download Image">
											<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
										</button>
									</div>
								</div>
								<div class="p-3">
									<p class="text-xs text-zinc-300 line-clamp-2" title={image.prompt}>{image.prompt}</p>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
