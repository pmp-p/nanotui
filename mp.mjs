import { loadMicroPython } from "./node_modules/@micropython/micropython-webassembly-pyscript/micropython.mjs";
console.log(loadMicroPython)
const mp = await loadMicroPython()
//mp.runPython("print('hello world')");

var py
var file

try {
    py = Bun.argv.pop()
    console.log(py)
    file = Bun.file(py)
} catch (x) {
    console.error("node ?")
}

const decoder = new TextDecoder();
mp.runPython(decoder.decode(await file.bytes()))

