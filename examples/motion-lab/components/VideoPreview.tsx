"use client";

import { Player } from "@remotion/player";
import { LaunchVideo } from "../video/LaunchVideo";
import { VIDEO, type LaunchBrief } from "../lib/brief";

export default function VideoPreview({ brief }: { brief: LaunchBrief }) {
  return <Player component={LaunchVideo} inputProps={{ brief }} durationInFrames={VIDEO.durationInFrames} fps={VIDEO.fps} compositionWidth={VIDEO.width} compositionHeight={VIDEO.height} controls autoPlay={false} loop={false} style={{ width: "100%", aspectRatio: "16 / 9" }} />;
}
