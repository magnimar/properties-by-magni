<script>
    const steps = [
        {
            title: "1. Skilgreindu þína leit",
            desc: "Veldu hverfi, verðbil, stærð og fleira.",
            icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10 text-blue-600"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0m-9.75 0h9.75" /></svg>`
        },
        {
            title: "2. Við leitum",
            desc: "Kerfið okkar leitar í gegnum allar fasteignir landsins.",
            icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10 text-blue-600"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>`
        },
        {
            title: "3. Fáðu daglega uppfærslu",
            desc: "Við sendum þér tölvupóst daglega með aðeins þeim eignum sem passa við þínar kröfur.",
            icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10 text-blue-600"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" /></svg>`
        }
    ];

    const benefits = [
        { title: "Sparaðu tíma", desc: "Ekki eyða tíma í að leita á fasteignasíðum. Við gerum það fyrir þig." },
        { title: "Ekki missa af neinu", desc: "Fáðu tölvupóst með öllum þeim eignum sem henta þínum kröfum." },
        { title: "Fáðu einungis eignir sem þú vilt", desc: "Fáðu daglega uppfærslu með aðeins þeim eignum sem passa þér fullkomlega." }
        ];
        </script>

<div class="min-h-screen font-sans text-gray-900 bg-white selection:bg-blue-100">
    <!-- Hero Section -->
    <section class="relative py-20 lg:py-32 overflow-hidden border-b border-gray-100">
        <!-- Top Right Navigation -->
        <div class="absolute top-6 right-6 md:top-10 md:right-10 z-50 flex flex-col sm:flex-row gap-4 sm:gap-6">
            <a href="/login" class="px-6 py-3 md:px-12 md:py-6 bg-white text-gray-800 border-2 border-gray-200 rounded-full font-bold text-lg md:text-2xl hover:bg-gray-50 transition-all shadow-md text-center">
                Innskráning
            </a>
            <a href="/register" class="px-6 py-3 md:px-12 md:py-6 bg-blue-600 text-white rounded-full font-bold text-lg md:text-2xl hover:bg-blue-700 transition-all shadow-md hover:shadow-lg transform hover:-translate-y-1 text-center">
                Búa til reikning
            </a>
        </div>

        <div class="container mx-auto px-6 relative z-10 mt-48 md:mt-24 lg:mt-32">
            <div class="max-w-4xl mx-auto text-center">
                <h1 class="text-5xl lg:text-7xl font-extrabold tracking-tight mb-8 leading-tight">
                    Fyrir fólk sem veit <span class="text-blue-600 italic">nákvæmlega</span> hvernig fasteign það vill.
                </h1>
            </div>
        </div>
        <!-- Decorative background element -->
        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-0 opacity-5 pointer-events-none">
            <svg viewBox="0 0 100 100" class="w-full h-full"><circle cx="50" cy="50" r="40" fill="currentColor" class="text-blue-600"/></svg>
        </div>
    </section>

    <!-- New Description Section -->
    <section class="py-16 bg-white">
        <div class="container mx-auto px-6">
            <div class="max-w-3xl mx-auto text-center">
                <p class="text-xl lg:text-2xl text-gray-600 leading-relaxed">
                    Þreytt/ur á að vakta fasteignasíðurnar endalaust og skrolla í gegnum eignir sem þú hefur engan áhuga á? Skilgreindu fasteignina sem þú vilt hjá okkur og fáðu daglegan tölvupóst með þeim eignum sem henta þér.
                </p>
            </div>
        </div>
    </section>

    <!-- How It Works -->
    <section class="py-24 bg-gray-50">
        <div class="container mx-auto px-6">
            <div class="grid md:grid-cols-3 gap-12 mb-20">
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

            <!-- Email Screenshot -->
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-gray-900">Sýnidæmi</h2>
            </div>
            <div class="max-w-4xl mx-auto rounded-3xl overflow-hidden shadow-2xl border border-gray-100">
                <img src="/email_screenshot.png" alt="Dæmi um tölvupóst" class="w-full h-auto object-cover" />
            </div>
        </div>
    </section>

    <!-- Feature Showcase (Filters Mockup) -->
    <section class="py-24">
        <div class="container mx-auto px-6 max-w-4xl">
            <div class="text-center mb-12">
                <h2 class="text-3xl lg:text-5xl font-bold mb-8 leading-tight">Sérsniðin leit</h2>
                <p class="text-lg text-gray-600 mb-8">
                    Í kerfinu er hægt að setja ýmsar kvaðir á eignir, eins og t.d.:
                </p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-2xl mx-auto">
                <ul class="space-y-4">
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Verðbil (Lágmark/Hámark)
                    </li>
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Fjöldi svefnherbergja
                    </li>
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Póstnúmer / Hverfi
                    </li>
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Götur/heimilisföng sem á að hunsa
                    </li>
                </ul>
                <ul class="space-y-4">
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Tegund eignar
                    </li>
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Svalir eða garður
                    </li>
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Bílskúr
                    </li>
                    <li class="flex items-center gap-3 text-gray-700 font-medium">
                        <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Fasteignamat
                    </li>
                </ul>
            </div>
        </div>
    </section>

    <!-- Benefits -->
    <section class="py-24 bg-blue-900 text-white">
        <div class="container mx-auto px-6 text-center">
            <h2 class="text-3xl lg:text-4xl font-bold mb-16">Hvers vegna að nota Properties by Magni?</h2>
            <div class="max-w-md mx-auto space-y-12">
                {#each benefits as benefit, i}
                    <div class="flex items-center gap-8 group">
                        <span class="text-6xl font-black text-blue-500 opacity-50 group-hover:opacity-100 transition-opacity">
                            {i + 1}
                        </span>
                        <div class="text-left">
                            <h3 class="text-3xl font-bold">{benefit.title}</h3>
                        </div>
                    </div>
                {/each}
            </div>
        </div>
    </section>

    <!-- Footer CTA -->
    <section class="py-24 bg-white text-center">
        <div class="container mx-auto px-6">
            <a href="/register" class="inline-block px-10 py-5 md:px-20 md:py-10 bg-blue-600 text-white rounded-full font-bold text-2xl md:text-4xl hover:bg-blue-700 transition-all shadow-2xl hover:scale-105 active:scale-95">
                Búa til reikning
            </a>
        </div>
    </section>

    <!-- Standard Footer -->
    <footer class="py-12 border-t border-gray-100 text-gray-500 bg-white">
        <div class="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8 text-center md:text-left">
            <div class="font-bold text-gray-900 text-xl tracking-tight">Properties by Magni</div>
            <p class="text-xs">© 2026 Properties by Magni. Allur réttur áskilinn.</p>
        </div>
    </footer>
</div>

<style>
    :global(html) {
        scroll-behavior: smooth;
    }
</style>
