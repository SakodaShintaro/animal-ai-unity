using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

/// <summary>
/// Headless build entry point, invoked as
///   Unity -batchmode -nographics -quit -projectPath . \
///         -executeMethod BuildScript.BuildLinux64 -buildPath /path/to/animalAI.x86_64
/// The scenes come from EditorBuildSettings so the build matches what the Editor
/// would produce from File > Build Settings.
/// </summary>
public static class BuildScript
{
    private static string GetArgument(string name)
    {
        string[] args = Environment.GetCommandLineArgs();
        int index = Array.IndexOf(args, name);
        if (index < 0 || index >= args.Length - 1)
        {
            throw new ArgumentException($"Missing command line argument {name}");
        }
        return args[index + 1];
    }

    public static void BuildLinux64()
    {
        string buildPath = GetArgument("-buildPath");
        BuildPlayerOptions options = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings
                .scenes.Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray(),
            locationPathName = buildPath,
            target = BuildTarget.StandaloneLinux64,
            options = BuildOptions.None
        };

        BuildReport report = BuildPipeline.BuildPlayer(options);
        BuildSummary summary = report.summary;
        Debug.Log(
            $"Build {summary.result}: {summary.totalErrors} errors, "
                + $"{summary.totalSize} bytes -> {buildPath}"
        );
        EditorApplication.Exit(summary.result == BuildResult.Succeeded ? 0 : 1);
    }
}
