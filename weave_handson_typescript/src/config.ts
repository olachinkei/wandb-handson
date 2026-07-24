import fs from "node:fs";
import path from "node:path";

import dotenv from "dotenv";
import { OpenAI } from "openai";
import { parse } from "yaml";
import * as weave from "weave";

dotenv.config();

export type ChatMessage = {
  role: "system" | "user" | "assistant";
  content: string;
};

type HandsonConfig = {
  openai?: {
    model?: string;
    image_model?: string;
    tts_model?: string;
  };
  default_temperature?: number;
  default_max_tokens?: number;
};

const DEFAULT_CONFIG: Required<HandsonConfig> = {
  openai: {
    model: "gpt-4o-mini",
    image_model: "gpt-image-1",
    tts_model: "gpt-4o-mini-tts",
  },
  default_temperature: 0.3,
  default_max_tokens: 150,
};

export function loadConfig(): HandsonConfig {
  const configPath = path.resolve(process.cwd(), "config.yaml");
  if (!fs.existsSync(configPath)) {
    return DEFAULT_CONFIG;
  }
  return parse(fs.readFileSync(configPath, "utf8")) as HandsonConfig;
}

export function getWeaveProjectName(): string {
  const entity = process.env.WANDB_ENTITY;
  const project = process.env.WANDB_PROJECT ?? "weave-handson-typescript";
  return entity ? `${entity}/${project}` : project;
}

export async function initWeave(settings?: Parameters<typeof weave.init>[1]): Promise<weave.WeaveClient> {
  return weave.init(getWeaveProjectName(), settings);
}

export function getOpenAIClient(): OpenAI {
  return new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });
}

export function getModelName(): string {
  return loadConfig().openai?.model ?? "gpt-4o-mini";
}

export function getImageModelName(): string {
  return loadConfig().openai?.image_model ?? "gpt-image-1";
}

export function getTtsModelName(): string {
  return loadConfig().openai?.tts_model ?? "gpt-4o-mini-tts";
}

export function getTemperature(): number {
  return loadConfig().default_temperature ?? DEFAULT_CONFIG.default_temperature;
}

export function getMaxTokens(): number {
  return loadConfig().default_max_tokens ?? DEFAULT_CONFIG.default_max_tokens;
}

export async function chatCompletion(
  messages: ChatMessage[],
  options: { temperature?: number; maxTokens?: number } = {}
): Promise<string> {
  const response = await getOpenAIClient().chat.completions.create({
    model: getModelName(),
    messages: messages as any,
    temperature: options.temperature ?? getTemperature(),
    max_tokens: options.maxTokens ?? getMaxTokens(),
  });
  return response.choices[0]?.message?.content ?? "";
}

export function printSection(title: string): void {
  console.log(`\n${"=".repeat(60)}`);
  console.log(title);
  console.log("=".repeat(60));
}
