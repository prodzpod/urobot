let world = null;
let areas = null;
let ret = [];
let currentArea = null;
d();
function d() {
    for (let t of document.getElementsByTagName("b")) if (t.innerText == "Connecting Areas") areas = t.parentElement.nextElementSibling.firstElementChild // should be the <p> tag
    world = document.getElementById("cosmos-title-text").innerText;
    if (areas != null && (world && !world.includes(":"))) {
        for (let g of areas.childNodes) {
            if (!g.tagName) continue;
            if (g.tagName.toUpperCase() == "A") {
                if (currentArea != null) ret.push(currentArea);
                currentArea = {"name": g.innerText};
            }
            else if (currentArea != null && g.tagName.toUpperCase() == "SPAN") {
                if (g.getAttribute("data-effect-params")) currentArea.effect = g.getAttribute("data-effect-params");
                if (g.getAttribute("data-lock-params")) currentArea.requirement = g.getAttribute("data-lock-params");
                if (g.getAttribute("data-chance-params")) currentArea.luck = true;
                if (
                    ((g.getAttribute("title")?.toLowerCase()?.trim()?.includes("opposite entrance") ?? false) && !g.getAttribute("title").toLowerCase().includes("unlocks"))
                    || (g.getAttribute("data-one-way-params") == "NoEntry")
                    || (g.getAttribute("title")?.toLowerCase()?.trim() == "Isolated location only accessible from the opposite side")
                    ) currentArea = null;
            }
        }
        if (currentArea != null) ret.push(currentArea);
        console.log(ret);
        let normals = ret.filter(x => !x.luck && !x.effect && !x.requirement);
        let txt = `"${world}": Maps(${normals.map(x => `"${x.name}"`).join(", ")})`;
        let notnormals = ret.filter(x => !(!x.luck && !x.effect && !x.requirement));
        if (notnormals.length > 0) {
            txt += ` + [${notnormals.map(v => {
                let subtxt = `Map("${v.name}", `;
                if (v.effect && v.requirement) subtxt += `{"${v.effect}", "${v.requirement}"}`;
                else if (v.effect) subtxt += `{"${v.effect}"}`;
                else if (v.requirement) subtxt += `{"${v.requirement}"}`;
                else subtxt += `set()`;
                if (v.luck) subtxt += `, set(), True`;
                subtxt += `)`;
                return subtxt;
            }).join(", ")}]`;
        }
        txt += ", \n";
        console.log(txt);
        navigator.clipboard.readText()
            .then(text => {
                if (text.includes(`"${world}": `)) return;
                navigator.clipboard.writeText(text + txt);
                document.getElementById("cosmos-title-text").style.color = "#0000FF";
            })
            .catch(err => {
                console.error('Failed to read clipboard contents: ', err);
            });
    }
    else setTimeout(d, 100);
}