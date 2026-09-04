/** Общие помощники по каталогу: одна реализация вместо копий по экранам. */
import type { Method } from './types';

export function methodsByCode(methods: Method[]): Record<string, Method> {
  const map: Record<string, Method> = {};
  for (const method of methods) map[method.code] = method;
  return map;
}

export function selectedMethods(basket: string[], byCode: Record<string, Method>): Method[] {
  return basket.map((code) => byCode[code]).filter((m): m is Method => Boolean(m));
}

export function impactsOf(method: Method): Record<string, number> {
  return {
    cpu: method.impact_cpu,
    gpu: method.impact_gpu,
    ram: method.impact_ram,
    vram: method.impact_vram,
    disk: method.impact_disk,
    network: method.impact_network,
  };
}
