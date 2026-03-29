<script>
    const steps = [
        {
            title: "1. Skilgreindu þína leit",
            desc: "Veldu hverfi, verðbil, stærð og fleira.",
            icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10 text-blue-600"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0m-9.75 0h9.75" /></svg>`
        },
        {
            title: "2. Við leitum",
            desc: "Kerfið okkar skannar allar helstu fasteignasíður landsins allan sólarhringinn.",
            icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10 text-blue-600"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>`
        },
        {
            title: "3. Fáðu daglega uppfærslu",
            desc: "Við sendum þér tölvupóst daglega með aðeins þeim eignum sem passa fullkomlega við þínar kröfur.",
            icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10 text-blue-600"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" /></svg>`
        }
    ];

    const benefits = [
        { title: "Sparaðu tíma", desc: "Ekki eyða tíma í að leita á mörgum síðum. Við gerum það fyrir þig." },
        { title: "Ekki missa af neinu", desc: "Við skönnum allar helstu fasteignasíður landsins." },
        { title: "Aðeins það sem þú vilt", desc: "Fáðu daglega uppfærslu með aðeins þeim eignum sem passa þér fullkomlega." },
        { title: "Faglegt og áreiðanlegt", desc: "Treystu á nákvæma og daglega uppfærslu frá sérhæfðu kerfi." }
    ];

    const testimonials = [
        { quote: "Ég var að leita að mjög sérstakri eign í Vesturbænum og var alveg búin að gefast upp. En Properties by Magni fann þessa frábæru eign sem ég hefði annars missa af.", author: "Sigríður, Vesturbæ" },
        { quote: "Þetta sparar mér svo mikinn tíma. Ég fær tölvupóst á hverjum degi með nákvæmlega því sem ég er að leita að. Það er svo auðvelt!", author: "Jón, Kópavogur" },
        { quote: "Frábær þjónusta fyrir alla sem eru að leita að nýju heimili. Mæli hiklaust með henni!", author: "Guðrún, Reykjavík" }
    ];
</script>

<div class="min-h-screen font-sans text-gray-900 bg-white selection:bg-blue-100">
    <!-- Hero Section -->
    <section class="relative py-20 lg:py-32 overflow-hidden border-b border-gray-100">
        <!-- Top Right Navigation -->
        <div class="absolute top-6 right-6 md:top-10 md:right-10 z-50 flex flex-col sm:flex-row gap-6">
            <a href="/login" class="px-12 py-6 bg-white text-gray-800 border-2 border-gray-200 rounded-full font-bold text-2xl hover:bg-gray-50 transition-all shadow-md text-center">
                Innskráning
            </a>
            <a href="/register" class="px-12 py-6 bg-blue-600 text-white rounded-full font-bold text-2xl hover:bg-blue-700 transition-all shadow-md hover:shadow-lg transform hover:-translate-y-1 text-center">
                Hefja leit
            </a>
        </div>

        <div class="container mx-auto px-6 relative z-10 mt-16 lg:mt-24">
            <div class="max-w-4xl mx-auto text-center">
                <h1 class="text-5xl lg:text-7xl font-extrabold tracking-tight mb-8 leading-tight">
                    Fyrir fólk sem veit <span class="text-blue-600 italic">nákvæmlega</span> hvað það vill.
                </h1>
                <p class="text-xl lg:text-2xl text-gray-600 mb-10 leading-relaxed max-w-2xl mx-auto">
                    Settu upp þínar nákvæmu kröfur. Þú þarft ekki lengur að vafra endalaust um fasteignasíður – við skönnum þær allar fyrir þig og sendum þér tölvupóst daglega með eignum sem passa fullkomlega við þig.
                </p>
            </div>
        </div>
        <!-- Decorative background element -->
        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-0 opacity-5 pointer-events-none">
            <svg viewBox="0 0 100 100" class="w-full h-full"><circle cx="50" cy="50" r="40" fill="currentColor" class="text-blue-600"/></svg>
        </div>
    </section>

    <!-- How It Works -->
    <section class="py-24 bg-gray-50">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl lg:text-4xl font-bold text-center mb-16">Hvernig það virkar</h2>
            <div class="grid md:grid-cols-3 gap-12">
                {#each steps as step}
                    <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center text-center group hover:shadow-md transition-shadow">
                        <div class="mb-6 p-4 bg-blue-50 rounded-full group-hover:scale-110 transition-transform">
                            {@html step.icon}
                        </div>
                        <h3 class="text-xl font-bold mb-4">{step.title}</h3>
                        <p class="text-gray-600">{step.desc}</p>
                    </div>
                {/each}
            </div>
        </div>
    </section>

    <!-- Feature Showcase (Filters Mockup) -->
    <section class="py-24">
        <div class="container mx-auto px-6 lg:flex items-center gap-16">
            <div class="lg:w-1/2 mb-12 lg:mb-0">
                <h2 class="text-3xl lg:text-5xl font-bold mb-8 leading-tight">Sérsniðin leit fyrir kröfuhart fólk</h2>
                <p class="text-lg text-gray-600 mb-8">
                    Við skiljum að þegar kemur að heimili þínu, þá skipta smáatriðin máli. Kerfið okkar leyfir þér að kafa dýpra en hefðbundnar fasteignasíður.
                </p>
                <ul class="space-y-4">
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Nákvæm hverfaskipting
                    </li>
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Sérkröfur eins og útsýni eða bílageymsla
                    </li>
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Sjálfvirkar tilkynningar um leið og eign kemur inn
                    </li>
                </ul>
            </div>
            <div class="lg:w-1/2">
                <div class="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
                    <div class="bg-gray-50 px-6 py-4 border-b border-gray-100 flex gap-2">
                        <div class="w-3 h-3 rounded-full bg-red-400"></div>
                        <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                        <div class="w-3 h-3 rounded-full bg-green-400"></div>
                    </div>
                    <div class="p-8 space-y-6">
                        <div class="space-y-2">
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Hverfi</label>
                            <div class="flex flex-wrap gap-2">
                                <span class="px-3 py-1 bg-blue-600 text-white text-sm rounded-md font-medium">Vesturbær (101, 107)</span>
                                <span class="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-md font-medium">Miðbær</span>
                                <span class="px-3 py-1 bg-blue-600 text-white text-sm rounded-md font-medium">Hlíðar (105)</span>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div class="space-y-2">
                                <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Verð (hámark)</label>
                                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200 font-mono text-sm">120.000.000 kr.</div>
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Stærð (lágmark)</label>
                                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200 font-mono text-sm">140 m²</div>
                            </div>
                        </div>
                        <div class="space-y-2">
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Sérkröfur</label>
                            <div class="space-y-2">
                                <div class="flex items-center gap-2"><div class="w-4 h-4 rounded bg-blue-600"></div> <span class="text-sm font-medium">Bílastæði í bílageymslu</span></div>
                                <div class="flex items-center gap-2"><div class="w-4 h-4 rounded bg-blue-600"></div> <span class="text-sm font-medium">Sérinnngangur</span></div>
                                <div class="flex items-center gap-2"><div class="w-4 h-4 border border-gray-300"></div> <span class="text-sm text-gray-400 font-medium">Lyfta</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Benefits -->
    <section class="py-24 bg-blue-900 text-white">
        <div class="container mx-auto px-6 text-center lg:text-left">
            <h2 class="text-3xl lg:text-4xl font-bold text-center mb-16">Hvers vegna að nota Properties by Magni?</h2>
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                {#each benefits as benefit}
                    <div class="p-8 rounded-2xl bg-blue-800/50 border border-blue-700/50 hover:bg-blue-800/70 transition-colors">
                        <h3 class="text-xl font-bold mb-4">{benefit.title}</h3>
                        <p class="text-blue-100 leading-relaxed text-sm">{benefit.desc}</p>
                    </div>
                {/each}
            </div>
        </div>
    </section>

    <!-- Testimonials -->
    <section class="py-24 bg-gray-50">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl lg:text-4xl font-bold text-center mb-16">Hvað segja notendur okkar?</h2>
            <div class="grid md:grid-cols-3 gap-8">
                {#each testimonials as item}
                    <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between italic hover:shadow-md transition-shadow">
                        <p class="text-gray-600 mb-6 leading-relaxed">"{item.quote}"</p>
                        <p class="text-sm font-bold text-gray-900 not-italic">— {item.author}</p>
                    </div>
                {/each}
            </div>
        </div>
    </section>

    <!-- Footer CTA -->
    <section class="py-24 bg-white text-center">
        <div class="container mx-auto px-6">
            <div class="max-w-4xl mx-auto bg-blue-50 p-12 lg:p-20 rounded-[3rem] border border-blue-100">
                <h2 class="text-4xl lg:text-5xl font-bold mb-6">Hefja þína leit í dag</h2>
                <p class="text-xl text-gray-600 mb-10">Sérsníða mína leit og fáðu daglega uppfærslu.</p>
                <a href="/register" class="inline-block px-12 py-5 bg-blue-600 text-white rounded-full font-bold text-xl hover:bg-blue-700 transition-all shadow-xl hover:scale-105 active:scale-95">
                    Hefja leit
                </a>
            </div>
        </div>
    </section>

    <!-- Standard Footer -->
    <footer class="py-12 border-t border-gray-100 text-gray-500 bg-white">
        <div class="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8 text-center md:text-left">
            <div class="font-bold text-gray-900 text-xl tracking-tight">Properties by Magni</div>
            <div class="flex flex-wrap justify-center gap-8 text-sm font-medium">
                <a href="#" class="hover:text-blue-600 transition-colors">Hafðu samband</a>
                <a href="#" class="hover:text-blue-600 transition-colors">Skilmálar</a>
                <a href="#" class="hover:text-blue-600 transition-colors">Persónuvernd</a>
            </div>
            <p class="text-xs">© 2024 Properties by Magni. Allur réttur áskilinn.</p>
        </div>
    </footer>
</div>

<style>
    :global(html) {
        scroll-behavior: smooth;
    }
</style>
