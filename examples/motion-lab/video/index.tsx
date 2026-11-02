import { Composition, registerRoot } from "remotion";
import { LaunchVideo } from "./LaunchVideo";
import { DEFAULT_BRIEF, VIDEO } from "../lib/brief";

function Root() {
  return <Composition id="LaunchDemo" component={LaunchVideo} durationInFrames={VIDEO.durationInFrames} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} defaultProps={{ brief: DEFAULT_BRIEF }} />;
}

registerRoot(Root);
